import psycopg
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

books_list = [(0)]

# Change username and database name to your liking and create them in postgresql
username = "postgres"
database = "book_store"

class mainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Book Store")
        
        self.conn = psycopg.connect(dbname = database, user = username)
        self.cursor = self.conn.cursor()
        
        self.cursor.execute("CREATE TABLE IF NOT EXISTS books(id INT, title VARCHAR(150), author VARCHAR(150), status INT);")

        self.set_border_width(10)

        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(True)
        self.add(self.grid)
        
        self.cursor.execute("SELECT * FROM books;")

        self.books_liststore = Gtk.ListStore(int, str, str, int)

        for book in self.cursor:
            self.books_liststore.append(list(book))

        self.treeview = Gtk.TreeView(model=self.books_liststore)
        self.treeview.connect("row_activated", self.on_selected_item)

        for i, column_title in enumerate(["ID", "Title", "Author", "Status"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            column.set_sort_column_id(0)
            self.treeview.append_column(column)

        self.scrollable_treelist = Gtk.ScrolledWindow()
        self.scrollable_treelist.set_vexpand(True)
        self.grid.attach(self.scrollable_treelist, 0, 0, 8, 10)
        self.scrollable_treelist.add(self.treeview)

        self.btn = Gtk.Button(label="Add Book")
        self.btn.connect("clicked", self.on_addBook_button_clicked)

        self.btn1 = Gtk.Button(label="Remove Book")
        self.btn1.connect("clicked", self.on_removeBook_button_clicked)
        
        self.grid.attach_next_to(self.btn, self.scrollable_treelist, Gtk.PositionType.BOTTOM, 1, 1)
        self.grid.attach_next_to(self.btn1, self.btn, Gtk.PositionType.RIGHT, 1, 1)

        self.show_all()
        
    def update_treeview_data(self):
        self.cursor.execute("SELECT * FROM books;")

        self.books_liststore = Gtk.ListStore(int, str, str, int)

        for book in self.cursor:
            self.books_liststore.append(list(book))

        self.treeview.set_model(self.books_liststore);

    def on_selected_item(self, widget, x, y):
        dialog = addBookDialog(self)
        model = widget.get_model()

        dialog.IdEntry.set_text(str(model[x][0]))
        dialog.IdEntry.props.editable = False
        
        dialog.TitleEntry.set_text(str(model[x][1]))
        dialog.AuthorEntry.set_text(str(model[x][2]))
        dialog.StatusEntry.set_text(str(model[x][3]))

        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            self.cursor.execute("UPDATE books SET (title, author, status)=(%s, %s, %s) WHERE ID=%s;", 
                (dialog.TitleEntry.get_text(), dialog.AuthorEntry.get_text(),
                 int(dialog.StatusEntry.get_text()), int(dialog.IdEntry.get_text())))
            self.conn.commit()
            
        self.update_treeview_data()

        dialog.destroy()

    def on_addBook_button_clicked(self, widget):
        dialog = addBookDialog(self)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            self.cursor.execute("INSERT INTO books (id, title, author, status) VALUES (%s, %s, %s, %s);", 
                (int(dialog.IdEntry.get_text()), dialog.TitleEntry.get_text(), 
                 dialog.AuthorEntry.get_text(), int(dialog.StatusEntry.get_text()), ))
            self.conn.commit()
            
        self.update_treeview_data()

        dialog.destroy()

    def on_removeBook_button_clicked(self, widget):
        dialog = removeBookDialog(self)
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            self.cursor.execute("DELETE FROM books WHERE ID=%s;", (dialog.IdEntry.get_text(), ))
            self.conn.commit()
        self.cursor.execute("SELECT * FROM books;")

        self.update_treeview_data()
        
        dialog.destroy()

class addBookDialog(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(title="Add new book", transient_for=parent, flags=0)
        self.set_resizable(False)
        self.set_border_width(10)
        
        self.IdLbl = Gtk.Label(label="Book id ")
        self.IdEntry = Gtk.Entry()
        self.TitleLbl = Gtk.Label(label="Title ")
        self.TitleEntry = Gtk.Entry()
        self.AuthorLbl = Gtk.Label(label="Author ")
        self.AuthorEntry = Gtk.Entry()
        self.StatusLbl = Gtk.Label(label="Status ")
        self.StatusEntry = Gtk.Entry()
        
        self.add_button("Submit", Gtk.ResponseType.OK)
        
        self.box = self.get_content_area()
        self.box.set_spacing(10)
        self.box.add(self.IdLbl)
        self.box.add(self.IdEntry)
        self.box.add(self.TitleLbl)
        self.box.add(self.TitleEntry)
        self.box.add(self.AuthorLbl)
        self.box.add(self.AuthorEntry)
        self.box.add(self.StatusLbl)
        self.box.add(self.StatusEntry)

        self.show_all()

class removeBookDialog(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(title="Remove book", transient_for=parent, flags=0)
        self.set_resizable(False)
        self.set_border_width(10)

        self.IdLbl = Gtk.Label(label="Book id ")
        self.IdEntry = Gtk.Entry()

        self.add_button("Submit", Gtk.ResponseType.OK)

        self.box = self.get_content_area()
        self.box.set_spacing(10)
        self.box.add(self.IdLbl)
        self.box.add(self.IdEntry)

        self.show_all()

win = mainWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
