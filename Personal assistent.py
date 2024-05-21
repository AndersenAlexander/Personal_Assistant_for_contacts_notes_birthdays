import json
import os
import re
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel, Listbox, Scrollbar, END


class PersonalAssistant:
    def __init__(self, data_dir='data', name='Personal Assistant'):
        """
        Initialize the Personal Assistant with default data directory and name.
        Load contacts and notes from JSON files.
        """
        self.name = name
        self.data_dir = data_dir
        self.contacts_file = os.path.join(data_dir, 'contacts.json')
        self.notes_file = os.path.join(data_dir, 'notes.json')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        self.contacts = self.load_data(self.contacts_file)
        self.notes = self.load_data(self.notes_file)

    def load_data(self, file_path):
        """
        Load data from a JSON file. If the file does not exist, return an empty list.
        """
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        else:
            return []

    def save_data(self, data, file_path):
        """
        Save data to a JSON file.
        """
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)

    def add_contact(self, name, address, phone, email, birthday):
        """
        Add a new contact to the contacts list.
        Validate email and phone number formats before adding.
        """
        if not self.validate_email(email):
            return "Invalid email format."
        if not self.validate_phone_number(phone):
            return "Invalid phone number format."
        contact = {'name': name, 'address': address,
                   'phone': phone, 'email': email, 'birthday': birthday}
        self.contacts.append(contact)
        self.save_data(self.contacts, self.contacts_file)
        return "Contact added successfully."

    def validate_email(self, email):
        """
        Validate the format of the email address using a regular expression.
        """
        pattern = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
        return re.match(pattern, email)

    def validate_phone_number(self, phone):
        """
        Validate the format of the phone number using a regular expression.
        """
        pattern = r'^\+?[\d\s]+$'
        return re.match(pattern, phone)

    def search_contacts(self, query):
        """
        Search for contacts by name, address, phone number, or email.
        """
        query = query.lower()
        return [contact for contact in self.contacts if
                query in contact['name'].lower() or
                query in contact['address'].lower() or
                query in contact['phone'].lower() or
                query in contact['email'].lower()]

    def edit_contact(self, name, new_data):
        """
        Edit an existing contact's information.
        """
        for contact in self.contacts:
            if contact['name'].lower() == name.lower():
                contact.update(new_data)
                self.save_data(self.contacts, self.contacts_file)
                return "Contact updated."
        return "Contact not found."

    def delete_contact(self, name):
        """
        Delete a contact by name.
        """
        original_length = len(self.contacts)
        self.contacts = [
            contact for contact in self.contacts if contact['name'].lower() != name.lower()]
        if len(self.contacts) < original_length:
            self.save_data(self.contacts, self.contacts_file)
            return "Contact deleted."
        return "Contact not found."

    def add_note(self, text, tags=None):
        """
        Add a new note with optional tags.
        """
        note = {'text': text, 'tags': tags if tags else []}
        self.notes.append(note)
        self.save_data(self.notes, self.notes_file)
        return "Note added with tags."

    def search_notes_by_text(self, query):
        """
        Search for notes by text content.
        """
        query = query.lower()
        return [note for note in self.notes if query in note['text'].lower()]

    def search_notes_by_tags(self, tag_query):
        """
        Search for notes by tag.
        """
        tag_query = tag_query.lower()
        return [note for note in self.notes if any(tag_query == tag.lower() for tag in note['tags'])]

    def search_notes(self, query):
        """
        Search for notes by text content or tags.
        """
        query = query.lower()
        return [note for note in self.notes if
                query in note['text'].lower() or
                any(query in tag.lower() for tag in note['tags'])]

    def edit_note(self, index, new_text, new_tags=None):
        """
        Edit an existing note's text and tags by index.
        """
        if 0 <= index < len(self.notes):
            self.notes[index]['text'] = new_text
            if new_tags:
                self.notes[index]['tags'] = new_tags
            self.save_data(self.notes, self.notes_file)
            return "Note updated."
        return "Note index out of range."

    def delete_note(self, index):
        """
        Delete a note by index.
        """
        if 0 <= index < len(self.notes):
            del self.notes[index]
            self.save_data(self.notes, self.notes_file)
            return "Note deleted."
        return "Note index out of range."

    def display_upcoming_birthdays(self, days):
        """
        Display a list of contacts whose birthdays are within a specified number of days from today.
        """
        today = datetime.now()
        upcoming_birthdays = []
        for contact in self.contacts:
            birthday = datetime.strptime(contact['birthday'], "%Y-%m-%d")
            this_year_birthday = birthday.replace(year=today.year)
            # Check if the birthday has already occurred this year
            if this_year_birthday < today:
                this_year_birthday = birthday.replace(year=today.year + 1)
            if 0 <= (this_year_birthday - today).days < days:
                upcoming_birthdays.append(contact)
        return upcoming_birthdays

    def get_all_birthdays(self):
        """
        Get all contacts' birthdays.
        """
        return sorted(self.contacts, key=lambda x: datetime.strptime(x['birthday'], "%Y-%m-%d"))


class GUI:
    def __init__(self, root, assistant):
        """
        Initialize the GUI with the root window and personal assistant instance.
        """
        self.root = root
        self.assistant = assistant
        root.title("Personal Assistant")

        # Create main menu
        self.main_menu = tk.Menu(root)
        root.config(menu=self.main_menu)

        # Add Contact menu
        self.contact_menu = tk.Menu(self.main_menu)
        self.main_menu.add_cascade(label="Contacts", menu=self.contact_menu)
        self.contact_menu.add_command(
            label="Add Contact", command=self.add_contact)
        self.contact_menu.add_command(
            label="View Contacts", command=self.view_contacts)
        self.contact_menu.add_command(
            label="Search Contact", command=self.search_contact)
        self.contact_menu.add_command(
            label="Edit Contact", command=self.edit_contact)
        self.contact_menu.add_command(
            label="Delete Contact", command=self.delete_contact)

        # Add Note menu
        self.note_menu = tk.Menu(self.main_menu)
        self.main_menu.add_cascade(label="Notes", menu=self.note_menu)
        self.note_menu.add_command(label="Add Note", command=self.add_note)
        self.note_menu.add_command(label="View Notes", command=self.view_notes)
        self.note_menu.add_command(
            label="Search Note by Text", command=self.search_note_by_text)
        self.note_menu.add_command(
            label="Search Note by Tags", command=self.search_note_by_tags)
        self.note_menu.add_command(
            label="Search Notes", command=self.search_notes)
        self.note_menu.add_command(label="Edit Note", command=self.edit_note)
        self.note_menu.add_command(
            label="Delete Note", command=self.delete_note)

        # Add Birthday menu
        self.birthday_menu = tk.Menu(self.main_menu)
        self.main_menu.add_cascade(label="Birthdays", menu=self.birthday_menu)
        self.birthday_menu.add_command(
            label="Display Upcoming Birthdays", command=self.display_upcoming_birthdays)
        self.birthday_menu.add_command(
            label="View Birthdays", command=self.view_birthdays)

    def add_contact(self):
        """
        GUI workflow to add a new contact.
        """
        name = simpledialog.askstring("Input", "Enter name:")
        address = simpledialog.askstring("Input", "Enter address:")
        phone = simpledialog.askstring("Input", "Enter phone number:")
        email = simpledialog.askstring("Input", "Enter email:")
        birthday = simpledialog.askstring(
            "Input", "Enter birthday (YYYY-MM-DD):")
        result = self.assistant.add_contact(
            name, address, phone, email, birthday)
        messagebox.showinfo("Result", result)

    def view_contacts(self):
        """
        GUI workflow to view all contacts.
        """
        contacts_window = Toplevel(self.root)
        contacts_window.title("All Contacts")

        listbox = Listbox(contacts_window, width=100, height=20)
        listbox.pack(side="left", fill="y")

        scrollbar = Scrollbar(contacts_window, orient="vertical")
        scrollbar.config(command=listbox.yview)
        scrollbar.pack(side="right", fill="y")

        listbox.config(yscrollcommand=scrollbar.set)

        for contact in self.assistant.contacts:
            listbox.insert(END, f"Name: {contact['name']}, Address: {contact['address']}, "
                           f"Phone: {contact['phone']}, Email: {
                               contact['email']}, "
                           f"Birthday: {contact['birthday']}")

    def search_contact(self):
        """
        GUI workflow to search for contacts.
        """
        query = simpledialog.askstring(
            "Input", "Enter search query for contacts:")
        results = self.assistant.search_contacts(query)
        if results:
            result_text = "\n".join([str(contact) for contact in results])
            messagebox.showinfo("Search Results", result_text)
        else:
            messagebox.showinfo("Search Results", "No contacts found.")

    def edit_contact(self):
        """
        GUI workflow to edit an existing contact.
        """
        name = simpledialog.askstring(
            "Input", "Enter the name of the contact to edit:")
        existing_contact = next(
            (contact for contact in self.assistant.contacts if contact['name'].lower() == name.lower()), None)
        if existing_contact:
            new_name = simpledialog.askstring(
                "Input", "Enter new name (or leave blank to keep current):", initialvalue=existing_contact['name'])
            new_address = simpledialog.askstring(
                "Input", "Enter new address (or leave blank to keep current):", initialvalue=existing_contact['address'])
            new_phone = simpledialog.askstring(
                "Input", "Enter new phone number (or leave blank to keep current):", initialvalue=existing_contact['phone'])
            new_email = simpledialog.askstring(
                "Input", "Enter new email (or leave blank to keep current):", initialvalue=existing_contact['email'])
            new_birthday = simpledialog.askstring(
                "Input", "Enter new birthday (YYYY-MM-DD) (or leave blank to keep current):", initialvalue=existing_contact['birthday'])
            new_data = {
                'name': new_name or existing_contact['name'],
                'address': new_address or existing_contact['address'],
                'phone': new_phone or existing_contact['phone'],
                'email': new_email or existing_contact['email'],
                'birthday': new_birthday or existing_contact['birthday']
            }
            result = self.assistant.edit_contact(name, new_data)
            messagebox.showinfo("Result", result)
        else:
            messagebox.showerror("Error", "Contact not found.")

    def delete_contact(self):
        """
        GUI workflow to delete a contact.
        """
        name = simpledialog.askstring(
            "Input", "Enter the name of the contact to delete:")
        result = self.assistant.delete_contact(name)
        messagebox.showinfo("Result", result)

    def add_note(self):
        """
        GUI workflow to add a new note.
        """
        text = simpledialog.askstring("Input", "Enter note text:")
        tags = simpledialog.askstring(
            "Input", "Enter tags separated by commas (optional):")
        result = self.assistant.add_note(
            text, [tag.strip() for tag in tags.split(',') if tag.strip()])
        messagebox.showinfo("Result", result)

    def view_notes(self):
        """
        GUI workflow to view all notes.
        """
        notes_window = Toplevel(self.root)
        notes_window.title("All Notes")

        listbox = Listbox(notes_window, width=100, height=20)
        listbox.pack(side="left", fill="y")

        scrollbar = Scrollbar(notes_window, orient="vertical")
        scrollbar.config(command=listbox.yview)
        scrollbar.pack(side="right", fill="y")

        listbox.config(yscrollcommand=scrollbar.set)

        for note in self.assistant.notes:
            listbox.insert(END, f"Note: {note['text']}, Tags: {
                           ', '.join(note['tags'])}")

    def search_note_by_text(self):
        """
        GUI workflow to search for notes by text.
        """
        query = simpledialog.askstring(
            "Input", "Enter search query for notes by text:")
        results = self.assistant.search_notes_by_text(query)
        if results:
            result_text = "\n".join([str(note) for note in results])
            messagebox.showinfo("Search Results", result_text)
        else:
            messagebox.showinfo("Search Results", "No notes found.")

    def search_note_by_tags(self):
        """
        GUI workflow to search for notes by tags.
        """
        tag_query = simpledialog.askstring(
            "Input", "Enter tag to search for notes by tags:")
        results = self.assistant.search_notes_by_tags(tag_query)
        if results:
            result_text = "\n".join([str(note) for note in results])
            messagebox.showinfo("Search Results", result_text)
        else:
            messagebox.showinfo("Search Results", "No notes found.")

    def search_notes(self):
        """
        GUI workflow to search for notes by text or tags.
        """
        query = simpledialog.askstring(
            "Input", "Enter search query for notes:")
        results = self.assistant.search_notes(query)
        if results:
            result_text = "\n".join([str(note) for note in results])
            messagebox.showinfo("Search Results", result_text)
        else:
            messagebox.showinfo("Search Results", "No notes found.")

    def edit_note(self):
        """
        GUI workflow to edit an existing note.
        """
        text_query = simpledialog.askstring(
            "Input", "Enter the text of the note you want to edit:")
        matching_notes = [
            note for note in self.assistant.notes if text_query.lower() in note['text'].lower()]
        if not matching_notes:
            messagebox.showinfo("Result", "No matching note found.")
        elif len(matching_notes) == 1:
            note = matching_notes[0]
            new_text = simpledialog.askstring(
                "Input", "Enter new text for the note (leave blank to keep current):", initialvalue=note['text'])
            new_tags = simpledialog.askstring(
                "Input", "Enter new tags separated by commas (leave blank to keep current):", initialvalue=",".join(note['tags']))
            if new_tags:
                note['tags'] = [tag.strip()
                                for tag in new_tags.split(',') if tag.strip()]
            if new_text:
                note['text'] = new_text
            result = self.assistant.edit_note(
                self.assistant.notes.index(note), note['text'], note['tags'])
            messagebox.showinfo("Result", result)
        else:
            result_text = "\n".join([f"{index + 1}: {note['text']} - Tags: {', '.join(
                note['tags'])}" for index, note in enumerate(matching_notes)])
            selected_index = simpledialog.askinteger(
                "Input", f"Multiple notes found. Please select one to edit by entering the corresponding number:\n{result_text}")
            if 0 < selected_index <= len(matching_notes):
                note = matching_notes[selected_index - 1]
                new_text = simpledialog.askstring(
                    "Input", "Enter new text for the note (leave blank to keep current):", initialvalue=note['text'])
                new_tags = simpledialog.askstring(
                    "Input", "Enter new tags separated by commas (leave blank to keep current):", initialvalue=",".join(note['tags']))
                if new_tags:
                    note['tags'] = [tag.strip()
                                    for tag in new_tags.split(',') if tag.strip()]
                if new_text:
                    note['text'] = new_text
                result = self.assistant.edit_note(
                    self.assistant.notes.index(note), note['text'], note['tags'])
                messagebox.showinfo("Result", result)

    def delete_note(self):
        """
        GUI workflow to delete a note.
        """
        try:
            index = simpledialog.askinteger(
                "Input", "Enter the index of the note to delete:")
            result = self.assistant.delete_note(index - 1)
            messagebox.showinfo("Result", result)
        except ValueError:
            messagebox.showerror(
                "Error", "Invalid index. Please enter a number.")

    def display_upcoming_birthdays(self):
        """
        GUI workflow to display upcoming birthdays.
        """
        try:
            days = simpledialog.askinteger(
                "Input", "Enter the number of days to check for upcoming birthdays:")
            results = self.assistant.display_upcoming_birthdays(days)
            if results:
                result_text = "\n".join([f"{contact['name']} has a birthday on {
                                        contact['birthday']}." for contact in results])
                messagebox.showinfo("Upcoming Birthdays", result_text)
            else:
                messagebox.showinfo("Upcoming Birthdays",
                                    f"No birthdays in the next {days} days.")
        except ValueError:
            messagebox.showerror(
                "Error", "Invalid input. Please enter a number.")

    def view_birthdays(self):
        """
        GUI workflow to view all birthdays.
        """
        birthdays_window = Toplevel(self.root)
        birthdays_window.title("All Birthdays")

        listbox = Listbox(birthdays_window, width=100, height=20)
        listbox.pack(side="left", fill="y")

        scrollbar = Scrollbar(birthdays_window, orient="vertical")
        scrollbar.config(command=listbox.yview)
        scrollbar.pack(side="right", fill="y")

        listbox.config(yscrollcommand=scrollbar.set)

        birthdays = self.assistant.get_all_birthdays()
        for contact in birthdays:
            listbox.insert(END, f"Name: {contact['name']}, Birthday: {
                           contact['birthday']}")


if __name__ == '__main__':
    root = tk.Tk()
    assistant = PersonalAssistant()
    gui = GUI(root, assistant)
    root.mainloop()
