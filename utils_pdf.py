import re
import json
import math

import pdfplumber

# output each page of a pdf as an image
def convert_pdf_to_imgs(pdf_path, dest_path_base, resolution=72):
    
    with pdfplumber.open(pdf_path) as pdf:
        """
        # by default resolution is 72 pts or pixels/in
        # if output rez is diff, then then the output values from the annotate.html app
        # will need to be scaled to match what PdfPlumner uses internally: 72 dpi
        # for reference only, here's a bit of code to show how that might be done

        scale = 72/150
        b = {"x0": 39.211987299025616,
            "y0": 341.5133346710862,
            "x1": 1219.8074086035338,
            "y1": 515.9374277123077
        }
        bb = (b["x0"]*scale, b["y0"]*scale, b["x1"]*scale, b["y1"]*scale)
        """

        for page_num, page in enumerate(pdf.pages, start=1):
            #im = page.within_bbox(bb).to_image(resolution=resolution).show()
            im = page.to_image(resolution=resolution)

            filename = f"{dest_path_base}_pg{page_num:02d}.png"
            im.save(filename, format="PNG")

    
# https://dev.to/rishabdugar/pdf-extraction-retrieving-text-and-tables-together-using-python-14c2
# for each page in a pdf, extract tables and create data obj that has cell data associated with the column header
# TODO: Only tested on a pdf with one table per page
def find_tables_from_pdf(pdf_path):
    documents = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            tables = page.find_tables()
            print(f"Page {page_num}: Found {len(tables)} tables.")
            for table in tables:

                # use x/horz boundaries to determine which header column each cell belongs to
                headers = []
                for cell in table.rows[0].cells:
                    # cell format: (x0, y0, x1, y1) or (l, t, r, b)
                    if cell: 
                        # Extract text within these exact bounds
                        text = page.within_bbox(cell).extract_text()
                        headers.append({
                            "text": text.strip() if text else "",
                            "x0": cell[0],
                            "x1": cell[2]
                        })

                data_rows = []
                # NOTE: starts after the first (header) row
                for row in table.rows[1:]:  # Limit to first 25 rows for testing purposes
                    row_data = {"menu_item": ""}
                    for cell in row.cells:
                        if cell:
                            cell_x0, cell_x1 = cell[0], cell[2]
                            cell_text = page.within_bbox(cell).extract_text()
                            cell_text = cell_text.strip() if cell_text else ""

                            # TODO: this is specific to the Chilis menu
                            row_data["menu_item"] = row_data[ headers[0]["text"] ] if headers[0]["text"] in row_data else "" # Default to first header for menu item

                            """
                            # NOTE: this is specific to the PDF structure and may need adjustment for other PDFs
                            if(cell_text == headers[1]["text"]): 
                                data_rows.pop()  # Remove the last row if it matches the header text
                                # TODO: capture headers[0] as a new category for the next rows until the next header is found
                                break  # Skip if the cell text matches a header
                            """
                            
                            # Find which header column this cell falls under
                            matched_header = "Unknown"
                            for header in headers:
                                # Check if the cell horizontally overlaps or aligns with the header
                                # Allowing a small 2-point tolerance for slight PDF alignment imperfections
                                if cell_x0 >= (header["x0"] - 2) and cell_x1 <= (header["x1"] + 2):
                                    matched_header = header["text"]
                                    break
                            
                            row_data[matched_header] = cell_text

                    data_rows.append(row_data)
                    #print(f"Extracted Row Data: {row_data}")

                for row in data_rows:
                    # Filter out None values and clean up whitespaces
                    cleaned_row = row # [str(cell).strip() for cell in row if cell is not None] # 
                    if cleaned_row:
                        row_text = json.loads( json.dumps(cleaned_row) ) # make into json obj
                        #print(f"Extracted Row: {row_text}")
                        documents.append({
                            "row": row_text,
                            "metadata": {"page": page_num, "source": pdf_path}
                        })

    return documents


# for each line of text in a pdf, extract info by applying the data_parsers to the lines
# also adds a bit of layout/positional info metadata
def extract_parsed_text_from_pdf(pdf_path, data_parsers, return_all=True):
    ret_lines = []

    # Extract text from PDF
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages[:], start=1):
            for line_num, lineraw in enumerate(page.extract_text_lines()):
                if(len(lineraw["text"]) == 0):
                    continue

                #HACK: skip header txt for testing
                if(line_num < -7):
                    continue

                line_data = get_data_by_parsers(lineraw, data_parsers)
                # NOTE: only lines with data found in the parsers will be processed
                if not return_all and not line_data:
                    continue

                # gather data from the chars in the line, usually font info
                line_top = round(lineraw["top"])
                line_left = round(lineraw["x0"])
                filtered_chars = [char for char in page.chars if round(char['top'], 0) == line_top]
                
                # Order the filtered characters by font size (size) descending
                # uses the first char to represent the entire line even though there may be chars in the line
                # with diff values
                # add a bit of data from elsewhere
                sorted_chars = sorted(filtered_chars, key=lambda x: x["size"], reverse=True)
                largest_char = sorted_chars[0]
                line_data.update({
                    "page": page_num, "line": line_num
                    , "line_top": line_top , "line_left": line_left
                    , "line_bottom": round(lineraw["bottom"]) , "line_right": round(lineraw["x1"])
                    , "font_size": largest_char["size"]
                    , "font_name": largest_char["fontname"]
                    , "source": pdf_path.lower()
                })

                line = lineraw["text"]
                #print(line)

                ret_lines.append({
                    "id": f"pg_{page_num}_ln_{line_num}",
                    "text": line,
                    "data": line_data
                })

        # add grouping lines by left position as new data point; these capture text indentations on the page and many times reflect a hierarchy, eg, descriptive text for a menu item
        ret_lines = add_group_linesXindent(ret_lines)

    return ret_lines


def add_group_linesXindent(pdfPlumber_lines, group_name="grp_indent_px", tolerance=2) :

    # group lines by left position, usually in pixels at 72 dpi
    # note the groups allow for some tolerance since things can be off a pixel or two but really belong in the same group
    # so abs_tol is in integer pixels to specify the tolerance, default to 2
    # these capture text indentations on the page and many times reflect a hierarchy, eg, descriptive text for a menu item

    grp_list = []
    for line in pdfPlumber_lines:
        line_left = line["data"]["line_left"]

        # use an existing grp if close enough, otherwise it will create a new group
        for grp in grp_list:
            if math.isclose(grp, line_left, abs_tol=tolerance):
                line_left = grp
                break

        # create a new group if need be
        if line_left not in grp_list:
            grp_list.append(line_left)

        # add the new grouping data
        line["data"].update({group_name:line_left}) # TODO: try_to_float?

    return pdfPlumber_lines


# tries to find metadata parsers and boxes for every line of text in a pdf
def extract_text_metadata_from_pdf(pdf_path, metadata_boxes, metadata_parsers):
    documents = []

    # Extract text from PDF
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages[:], start=1):
            for line_num, lineraw in enumerate(page.extract_text_lines()):
                if(len(lineraw["text"]) == 0):
                    continue

                pg_metadata_boxes = metadata_boxes.get(f"pg{page_num}", []) # used to grab relevant box data for this page
                metadata = get_metadata(lineraw, pg_metadata_boxes, metadata_parsers)
                metadata.update({"page": page_num, "line": line_num, "source": pdf_path.lower()})

                line_text = lineraw["text"]
                #print(line)

                documents.append({
                    "id": f"pg_{page_num}_ln_{line_num}",
                    "row": line_text,
                    "metadata": metadata # name came from the intention for this to be put in a vector DB
                })

    return documents


# intended for javascript consumption, try to make numeric vals where possible instead of strings
# all numeric vals in javascript are floats, no such thing as ints really
def to_js_type(value):
    try:
        return float(value)
    except ValueError:
        return value


def get_metadata(lineobj, boxes = [], metadata_parsers = []):

    ret = {}

    ret.update( get_data_by_boxes(lineobj, boxes) )
    ret.update( get_data_by_parsers(lineobj, metadata_parsers) )

    return ret


# parsers are a list of uncompiled regex pattern strings
# for each parsing regex patter, check to see if lineobj has any matches and if so, capture the parser's associated data
def get_data_by_parsers(lineobj, data_parsers = []):

    ret = {} # default dict obj

    # pre-compile so it only happens once
    parsers = [re.compile(pattern) for pattern in data_parsers]

    for i, pattern in enumerate(parsers):
        match = re.search(pattern, lineobj["text"])
        if match:

            # extract all named groups as a dictionary
            groups_dict = match.groupdict()
            # add the regex groups and their values
            
            for k,v in groups_dict.items():
                 #ret.update({k.replace("_", " "): try_to_float(v)}) # NOTE: keys have underscores replaced with the intention of the phrasing to be more natural
                 ret.update({k: to_js_type(v)})

    return ret


# for each box, check to see if lineobj is within it and if so, capture the box's associated data
def get_data_by_boxes(lineobj, boxes = []):
    """
    # example of box obj found in the boxes list
    {
        "id": "7989e28c-542b-42b9-9af7-7d5f3256dbf3",
        "text": "spicy",
        "x0": 5.1, "y0": 581.2, "x1": 347.3, "y1": 621.4
    }    
    """
    ret = {} # default dict obj

    for box_num, box in enumerate(boxes):

        if( lineobj["x0"] >= box["x0"] #TODO: add horz x checks
            and lineobj["top"] >= box["y0"]
            and lineobj["bottom"] <= box["y1"]
        ):

            """
            # format for metadata (where/filtering) usage in chromadb
            # needs to handle strings:
                "beverages: soda | fountain drinks | tea | coffee | lemonade | water | shake"
                "beverages: wine"
            to (from pipe delimiter, make string items in a list, remove extra whitespace):
                "beverages": ["soda","fountain drinks","tea","coffee","lemonade","water","shake"]
                "beverages": ["wine"]
            """
            dict = {
                k.strip(): [item.strip() for item in v.strip().split("|") ] # 
                for pair in box["text"].split(";") 
                for k, v in [pair.split(":")]
            }
            ret.update(dict)

    return ret

# example code but not used yet
def x():
    with pdfplumber.open("./data/in/ChilisMenu.pdf") as pdf:
        for i, page in enumerate(pdf.pages[:1]):
            print(f"--- Page {i+1} ---")
            
            # Use extract_words to get structural coordinates while keeping metadata
            words = page.extract_words(extra_attrs=["fontname", "size"])
            
            for word in words:
                # Filter words that match specific criteria (e.g., Large or Bold text)
                if word["size"] > 14 or "Bold" in word["fontname"]:
                    print(f"[HEADER/BOLD] {word['text']} (Font: {word['fontname']}, Size: {word['size']:.1f})")
                else:
                    print(f"{word['text']} (Font: {word['fontname']}, Size: {word['size']:.1f})")
                    #print(f"{word['text']}", end=" ")
            print("\n")
