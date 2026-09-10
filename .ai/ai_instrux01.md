* GOAL:  show Python code that can demonstrate parsing a PDF and storing it in a local database so that later an ai chat model will use this as the context to answer questions

* RULES
- You are an expert Python developer
- use libaries: ollama, chromadb, pdfplumber
- all must run locally
- use chromadb for persistent db
- use "nomic-embed-text" as the embedding model

* show example code that does the following:
- pdfplumber will extract table data from specified pdf file
- must include the vectors data
- put the results into chromadb for persistent db

* show example code that does the following:
- using ollama.chat show how to use the chromadb to answer questions



--------------------------------

- you are an expert web app developer
- provide complete code for single page interactive app using Annotorious library to define multiple box regions
- additional information about Annotorious usage can be found here: https://annotorious.dev/guides/annotating-images/
- use common browser technologies (HTML, javascript, css) 
- it should have create/edit/delete functionality for all the defined boxes using keyboard shortcuts
- have a dialog for the user to choose the image
- provide an Export button to copy the data to the clipboard- each box should have user-editable text associated with it
-- the export data format should follow the json pattern for each box item:
`
{
    id: '[guid value]',
    text: "[user entered text value]",
    x0: [left],
    y0: [top],
    x1: [right],
    y1: [bottom],
}
`
- break out the html and javascript into their own output
- break out the css/styles into another code output
- use the following code for loading Annotorious code and stylesheets:
`
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@annotorious/annotorious@latest/dist/annotorious.css">
    <script src="https://cdn.jsdelivr.net/npm/@annotorious/annotorious@latest/dist/annotorious.js"></script>
`
- A sidebar on the right lists all existing boxes.
- Clicking a list item selects that annotation in the image for editing.
- The list updates automatically when boxes are created, edited, or deleted.
- The image should have interactive zoom/panning functionality


