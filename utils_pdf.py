import json
import pdfplumber

def convert_pdf_to_imgs(pdf_path, dest_path_base, resolution=150):
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            im = page.to_image(resolution=resolution)
            filename = f"{dest_path_base}_pg{page_num:02d}.png"
            im.save(filename, format="PNG")

    

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
                    # cell format: (x0, y0, x1, y1)
                    if cell: 
                        # Extract text within these exact bounds
                        text = page.within_bbox(cell).extract_text()
                        headers.append({
                            "text": text.strip() if text else "",
                            "x0": cell[0],
                            "x1": cell[2]
                        })

                data_rows = []
                for row in table.rows[1:]:  # Limit to first 25 rows for testing purposes
                    row_data = {"menu_item": ""}
                    for cell in row.cells:
                        if cell:
                            cell_x0, cell_x1 = cell[0], cell[2]
                            cell_text = page.within_bbox(cell).extract_text()
                            cell_text = cell_text.strip() if cell_text else ""

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


def find_text_from_pdf(pdf_path):
    documents = []

    # Step 1: Extract text from PDF
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            lines = page.extract_text().split("\n")
            if lines:
                for line_num, line in enumerate(lines):
                    #print(line)

                    documents.append({
                        "id": f"pg_{page_num}_ln_{line_num}",
                        "row": line,
                        "metadata": {"page": page_num, "source": pdf_path}
                    })

    return documents
