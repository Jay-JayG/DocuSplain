import fitz
import tkinter as tk
from tkinter import *
from tkinter import ttk
from miner import PDFMiner
from tkinter import filedialog as fd
import os
import webscraper

# Open a PDF file
pdf_document = fitz.open("Business Model.pdf")

# Select the first page of the PDF (page number starts from 0)
page = pdf_document[0]


class PDFViewer:
    # initializing the __init__ / special method
    def __init__(self, master):
        self.initialize_variables()
        self.create_main_window(master)
        self.create_menu()
        self.create_frames()
        self.create_widgets()


    def initialize_variables(self):
        # path for the pdf doc
        self.path = None
        # state of the pdf doc, open or closed
        self.fileisopen = None
        # author of the pdf doc
        self.author = None
        # name for the pdf doc
        self.name = None
        # the current page for the pdf
        self.current_page = 0
        # total number of pages for the pdf doc
        self.numPages = None

    def create_main_window(self, master):
        # creating the window
        self.master = master
        # gives title to the main window
        self.master.title('PDF Viewer')
        # gives dimensions to main window
        self.master.geometry('1360x880')

    def create_menu(self):
        # creating the menu
        self.menu = Menu(self.master)
        # adding it to the main window
        self.master.config(menu=self.menu)
        # creating a sub menu
        self.filemenu = Menu(self.menu)
        # giving the sub menu a label
        self.menu.add_cascade(label="File", menu=self.filemenu)
        # adding two buttons to the sub menus
        self.filemenu.add_command(label="Open File", command=self.open_file)
        self.filemenu.add_command(label="Exit", command=self.master.destroy)

    def create_frames(self):
        self.create_top_frames()
        self.create_bottom_frames()

    def create_top_frames(self):
        # creating the top frame
        self.top_frame = ttk.Frame(self.master)
        # placing the frame using inside main window using grid()
        self.top_frame.grid(row=0, column=0, sticky=(N, S, E, W))
        # the frame will not propagate
        self.top_frame.grid_propagate(False)

    def create_bottom_frames(self):
        # creating the bottom frame
        self.bottom_frame = ttk.Frame(self.master, width=580, height=50)
        # placing the frame using inside main window using grid()
        self.bottom_frame.grid(row=1, column=0)
        # the frame will not propagate
        self.bottom_frame.grid_propagate(False)

    def create_widgets(self):
        self.create_canvas()
        self.create_text_widget()
        self.create_output_widget()
        self.create_context_menu()
        self.create_scrollbars()
        self.create_buttons()
        self.create_page_label()
        self.create_input_text_widget()

        # inserting both vertical and horizontal scrollbars to the canvas
        self.output.configure(yscrollcommand=self.scrolly.set, xscrollcommand=self.scrollx.set)
        # binding the resize function to the window resize event
        self.master.bind('<Configure>', self.resize)

    def create_canvas(self):
        # creating the canvas for display the PDF pages
        self.output = Canvas(self.top_frame, bg='#ECE8F3', width=560, height=435)
        # adding the canvas
        self.output.grid(row=0, column=0, rowspan=2, padx=(0, 5), sticky=(N, S, E, W))

    def create_text_widget(self):
        # creating a Text widget for displaying text content
        self.text_widget = Text(self.top_frame, wrap='none', bg='#ECE8F3', width=40, height=20)
        self.text_widget.grid(row=0, column=1, padx=5, pady=5, sticky=(N, S, E, W))
        # binding right-click event to show context menu
        self.text_widget.bind("<Button-3>", self.show_context_menu)

    def create_output_widget(self):
        # creating a Text widget for displaying the output text from the LLM
        self.output_text_widget = Text(self.top_frame, wrap='none', bg='#ECE8F3', width=40, height=20)
        self.output_text_widget.grid(row=0, column=2, padx=5, sticky=(N, S, E, W))

    def create_input_text_widget(self):
        # creating a Text widget for displaying the output text from the LLM
        self.input_text_widget = Text(self.top_frame, wrap='none', bg='#ECE8F3', width=20, height=1)
        self.input_text_widget.grid(row=1, column=2, padx=5, sticky=(N, S, E, W))

    def create_context_menu(self):
        # creating a context menu
        self.context_menu = Menu(self.text_widget, tearoff=0)
        self.context_menu.add_command(label="Copy", command=self.copy_text)

    def create_scrollbars(self):
        # creating a vertical scrollbar
        self.scrolly = Scrollbar(self.top_frame, orient=VERTICAL, command=self.output.yview)
        # adding the scrollbar
        self.scrolly.grid(row=0, column=0, sticky=(N, S, E))
        # creating a horizontal scrollbar
        self.scrollx = Scrollbar(self.top_frame, orient=HORIZONTAL, command=self.output.xview)
        # adding the scrollbar
        self.scrollx.grid(row=1, column=0, sticky=(W, E))
        # configuring the horizontal scrollbar to the canvas
        self.scrolly.configure(command=self.output.yview)
        # configuring the vertical scrollbar to the canvas
        self.scrollx.configure(command=self.output.xview)
        # configuring the vertical scrollbar to the canvas
        self.scrollx.configure(command=self.output.xview)

    def create_button_icons(self):
        # loading the button icons
        self.uparrow_icon = PhotoImage(file='uparrow.png')
        self.downarrow_icon = PhotoImage(file='downarrow.png')
        # resizing the icons to fit on buttons
        self.uparrow = self.uparrow_icon.subsample(3, 3)
        self.downarrow = self.downarrow_icon.subsample(3, 3)


    def create_up_button(self):
        # creating an up button with an icon
        self.upbutton = ttk.Button(self.top_frame, image=self.uparrow, command=self.previous_page)
        # adding the button
        self.upbutton.grid(row=3, column=0, padx=(270, 5), pady=8)

    def create_down_button(self):
        # creating a down button with an icon
        self.downbutton = ttk.Button(self.top_frame, image=self.downarrow, command=self.next_page)
        # adding the button
        self.downbutton.grid(row=3, column=2, pady=8)

    def create_input_button(self):
        self.input_button = ttk.Button(self.top_frame, text="Generate", command=lambda: self.on_button_click(self.input_text_widget.get("1.0", tk.END)))
        # Position of button
        self.input_button.grid(row=1, column=3, pady=10)

    def create_buttons(self):
        self.create_button_icons()
        self.create_up_button()
        self.create_down_button()
        self.create_input_button()

    def create_page_label(self):
        # label for displaying page numbers
        self.page_label = ttk.Label(self.top_frame, text='page')
        # adding the label
        self.page_label.grid(row=3, column=1, padx=5)

    # External commands

    def open_file(self):
        # open the file dialog
        filepath = fd.askopenfilename(title='Select a PDF file', initialdir=os.getcwd(), filetypes=(('PDF', '*.pdf'),))
        # checking if the file exists
        if filepath:
            # declaring the path
            self.path = filepath
            # extracting the pdf file from the path
            filename = os.path.basename(self.path)
            # passing the path to PDFMiner
            self.miner = PDFMiner(self.path)
            # getting data and numPages
            data, numPages = self.miner.get_metadata()
            # setting the current page to 0
            self.current_page = 0
            # checking if numPages exists
            if numPages:
                # getting the title
                self.name = data.get('title', filename[:-4])
                # getting the author
                self.author = data.get('author', None)
                self.numPages = numPages
                # setting fileopen to True
                self.fileisopen = True
                # calling the display_page() function
                self.display_page()
                # replacing the window title with the PDF document name
                self.master.title(self.name)

    def display_page(self):
        # checking if numPages is less than current_page and if current_page is less than
        # or equal to 0
        if 0 <= self.current_page < self.numPages:
            # getting the page using get_page() function from miner
            self.img_file = self.miner.get_page(self.current_page)
            # inserting the page image inside the Canvas
            self.output.create_image(0, 0, anchor='nw', image=self.img_file)
            # the variable to be stringified
            self.stringified_current_page = self.current_page + 1
            # updating the page label with number of pages
            self.page_label['text'] = str(self.stringified_current_page) + ' of ' + str(self.numPages)
            # creating a region for inserting the page inside the Canvas
            region = self.output.bbox(ALL)
            # making the region to be scrollable
            self.output.configure(scrollregion=region)
            # getting the text content of the page using get_text() function from miner
            text_content = self.miner.get_text(self.current_page)
            # deleting previous text from the Text widget
            self.text_widget.delete(1.0, END)
            # inserting the text content inside the Text widget
            self.text_widget.insert(INSERT, text_content)

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def copy_text(self):
        selected_text = self.text_widget.get(SEL_FIRST, SEL_LAST)
        if selected_text:
            self.master.clipboard_clear()
            self.master.clipboard_append(selected_text)
            self.master.update()

    def next_page(self):
        # checking if file is open
        if self.fileisopen:
            # checking if current_page is less than or equal to numPages-1
            if self.current_page <= self.numPages - 1:
                # updating the page with value 1
                self.current_page += 1
                # displaying the new page
                self.display_page()

    def previous_page(self):
        # checking if fileisopen
        if self.fileisopen:
            # checking if current_page is greater than 0
            if self.current_page > 0:
                # decrementing the current_page by 1
                self.current_page -= 1
                # displaying the previous page
                self.display_page()

    def resize(self, event):
        # Get the width and height of the application window
        window_width = self.master.winfo_width()
        window_height = self.master.winfo_height()

        # Set the width and height of the top_frame based on window size
        self.top_frame.config(width=window_width, height=window_height)

    def on_button_click(self, input_text):
        text = webscraper.insert_text(input_text)
        self.output_text_widget.delete(1.0, tk.END)  # Clear previous content
        self.output_text_widget.insert(tk.END, text)

# creating the root window using Tk() class
root = Tk()
root.title("PDF Viewer")
# instantiating/creating object app for class PDFViewer
app = PDFViewer(root)

# calling the mainloop to run the app infinitely until user closes it
root.mainloop()
