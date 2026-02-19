import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import hashlib
import os
import threading

class ISOVerifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple ISO Verifier")
        self.root.geometry("600x450")
        self.root.resizable(False, False)

        # Style customization
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#ccc")
        self.style.configure("TLabel", padding=6, font=("Helvetica", 10))
        self.style.configure("Header.TLabel", font=("Helvetica", 14, "bold"))

        # Variables
        self.iso_path = tk.StringVar()
        self.checksum_path = tk.StringVar()
        self.pasted_checksum = tk.StringVar()
        self.status_message = tk.StringVar(value="Ready to verify.")
        self.is_verifying = False

        self.create_widgets()

    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self.root, padding="20 20 20 10")
        header_frame.pack(fill=tk.X)
        header_label = ttk.Label(header_frame, text="Simple ISO Verifier", style="Header.TLabel")
        header_label.pack()
        subtitle = ttk.Label(header_frame, text="Check if your downloaded file is safe and original.", foreground="gray")
        subtitle.pack()

        # Input Frame
        input_frame = ttk.Frame(self.root, padding="20 10 20 10")
        input_frame.pack(fill=tk.X)

        # 1. Select ISO File
        ttk.Label(input_frame, text="Step 1: Select the ISO/File you downloaded").pack(anchor=tk.W)
        iso_entry_frame = ttk.Frame(input_frame)
        iso_entry_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.iso_entry = ttk.Entry(iso_entry_frame, textvariable=self.iso_path, state="readonly")
        self.iso_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_iso_btn = ttk.Button(iso_entry_frame, text="Browse File...", command=self.browse_iso)
        browse_iso_btn.pack(side=tk.RIGHT)

        # 2. Select Authenticity Source
        ttk.Label(input_frame, text="Step 2: Provide the Checksum (SHA256)").pack(anchor=tk.W)
        
        # Tabs for Source
        self.notebook = ttk.Notebook(input_frame)
        self.notebook.pack(fill=tk.X, pady=(5, 15))

        # Tab 1: Paste Text
        tab1 = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab1, text="Paste Hash Text")
        
        ttk.Label(tab1, text="Paste the SHA256 hash here (e.g., from the download page):").pack(anchor=tk.W)
        self.hash_entry = ttk.Entry(tab1, textvariable=self.pasted_checksum)
        self.hash_entry.pack(fill=tk.X, pady=(5, 0))

        # Tab 2: Select Checksum File
        tab2 = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab2, text="Select Checksum File")
        
        ttk.Label(tab2, text="Select the 'sha256sum.txt' file if you downloaded one:").pack(anchor=tk.W)
        checksum_file_frame = ttk.Frame(tab2)
        checksum_file_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.checksum_file_entry = ttk.Entry(checksum_file_frame, textvariable=self.checksum_path, state="readonly")
        self.checksum_file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_checksum_btn = ttk.Button(checksum_file_frame, text="Browse File...", command=self.browse_checksum)
        browse_checksum_btn.pack(side=tk.RIGHT)

        # Verify Button
        action_frame = ttk.Frame(self.root, padding="20 10")
        action_frame.pack(fill=tk.X)
        
        self.verify_btn = ttk.Button(action_frame, text="VERIFY INTEGRITY", command=self.start_verification)
        self.verify_btn.pack(fill=tk.X, ipady=10)

        # Progress and Status
        status_frame = ttk.Frame(self.root, padding="20 10")
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.progress = ttk.Progressbar(status_frame, orient=tk.HORIZONTAL, mode='determinate')
        self.progress.pack(fill=tk.X, pady=(0, 10))

        self.status_label = ttk.Label(status_frame, textvariable=self.status_message, anchor="center")
        self.status_label.pack(fill=tk.X)

    def browse_iso(self):
        filename = filedialog.askopenfilename(title="Select ISO File")
        if filename:
            self.iso_path.set(filename)
            self.status_message.set("Ready to verify.")
            self.status_label.config(foreground="black")

    def browse_checksum(self):
        filename = filedialog.askopenfilename(title="Select Checksum File", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if filename:
            self.checksum_path.set(filename)

    def start_verification(self):
        if self.is_verifying:
            return

        iso_file = self.iso_path.get()
        if not iso_file or not os.path.exists(iso_file):
            messagebox.showerror("Error", "Please select a valid ISO file first.")
            return

        # Determine source of hash
        expected_hash = ""
        current_tab = self.notebook.index(self.notebook.select())
        
        if current_tab == 0: # Paste Hash
            expected_hash = self.pasted_checksum.get().strip()
            if not expected_hash:
                messagebox.showerror("Error", "Please paste a SHA256 hash.")
                return
        else: # File Source
            checksum_file = self.checksum_path.get()
            if not checksum_file or not os.path.exists(checksum_file):
                messagebox.showerror("Error", "Please select a valid checksum file.")
                return
            
            # Parse the checksum file
            try:
                expected_hash = self.parse_checksum_file(checksum_file, iso_file)
                if not expected_hash:
                    messagebox.showerror("Error", "Could not find a hash for the selected ISO in the checksum file.")
                    return
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read checksum file: {e}")
                return

        # Start threading
        self.is_verifying = True
        self.verify_btn.config(state="disabled")
        self.input_lock(True)
        self.status_message.set("Verifying... This may take a moment for large files.")
        self.progress['value'] = 0
        
        thread = threading.Thread(target=self.verify_process, args=(iso_file, expected_hash))
        thread.daemon = True
        thread.start()

    def input_lock(self, lock):
        state = "disabled" if lock else "normal"
        # Since we used readonly for file entries, they remain 'readonly' not 'disabled' strictly or 'normal'
        pass # Simplified for now, just disabling the verify button is enough to prevent double submission

    def parse_checksum_file(self, checksum_path, iso_path):
        iso_filename = os.path.basename(iso_path)
        with open(checksum_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read().strip()
            
            # Case 1: The file contains ONLY the hash (and maybe whitespace)
            # A SHA256 hash is 64 hex characters.
            if len(content) == 64 and all(c in '0123456789abcdefABCDEF' for c in content):
                return content

            # Case 2: Standard SHA256SUMS file format
            # Format: <hash>  <filename>
            # OR: <hash> *<filename>
            
            # Reset file pointer to read line by line
            f.seek(0)
            for line in f:
                line = line.strip()
                if not line: continue
                
                parts = line.split(maxsplit=1)
                if len(parts) == 2:
                    line_hash = parts[0]
                    line_filename = parts[1]
                    
                    # Check if it looks like a hash
                    if len(line_hash) == 64 and all(c in '0123456789abcdefABCDEF' for c in line_hash):
                        # Clean up filename (remove * for binary indicator)
                        if line_filename.startswith('*'):
                            line_filename = line_filename[1:]
                            
                        # flexible matching: exact match OR if the line filename is just the name (no path)
                        if line_filename == iso_filename or os.path.basename(line_filename) == iso_filename:
                            return line_hash
                            
            # Case 3: Iterate again and look for ANY 64-char hex string if we verified the filename is present in the line
                # Rationale: Sometimes formats are weird.
                if iso_filename in line:
                    # Try to find a 64-char hex string in the line
                    import re
                    match = re.search(r'\b[0-9a-fA-F]{64}\b', line)
                    if match:
                        return match.group(0)

        return None

    def verify_process(self, iso_file, expected_hash):
        try:
            file_size = os.path.getsize(iso_file)
            sha256_hash = hashlib.sha256()
            
            chunk_size = 65536 # 64KB chunks
            
            bytes_read = 0
            with open(iso_file, "rb") as f:
                for byte_block in iter(lambda: f.read(chunk_size), b""):
                    sha256_hash.update(byte_block)
                    bytes_read += len(byte_block)
                    
                    # Update progress
                    # Use self.root.after to safely update GUI from thread
                    if file_size > 0:
                        progress_val = (bytes_read / file_size) * 100
                        self.root.after(0, self.update_progress, progress_val)

            calculated_hash = sha256_hash.hexdigest()
            
            # Compare (case insensitive)
            match = calculated_hash.lower() == expected_hash.lower()
            
            # Schedule result display
            self.root.after(0, lambda: self.verification_complete(match, calculated_hash))

        except Exception as e:
            self.root.after(0, lambda: self.verification_error(str(e)))

    def update_progress(self, value):
        self.progress['value'] = value

    def verification_complete(self, match, calculated_hash):
        self.is_verifying = False
        self.verify_btn.config(state="normal")
        
        if match:
            self.status_message.set("SUCCESS! The file is authentic.")
            self.status_label.config(foreground="green", font=("Helvetica", 12, "bold"))
            messagebox.showinfo("Result", "MATCH!\nThe file's SHA256 hash matches the expected value.\nIt is safe to use.")
        else:
            self.status_message.set("WARNING! HASH MISMATCH.")
            self.status_label.config(foreground="red", font=("Helvetica", 12, "bold"))
            messagebox.showerror("Result", f"MISMATCH!\n\nCalculated: {calculated_hash}\nExpected: (Provided Input)\n\nThe file may be corrupted or modified.")

    def verification_error(self, error_msg):
        self.is_verifying = False
        self.verify_btn.config(state="normal")
        self.status_message.set("Error during verification.")
        messagebox.showerror("Error", f"An error occurred: {error_msg}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ISOVerifierApp(root)
    root.mainloop()
