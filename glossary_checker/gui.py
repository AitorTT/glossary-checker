"""Modern Tkinter GUI for Glossary Checker."""
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import threading
from .core import GlossaryChecker
from .exporters import export_to_excel, export_summary_text


class GlossaryCheckerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Glossary Compliance Checker")
        self.root.geometry("1100x700")
        self.root.configure(bg='#1e1e2e')
        
        # Store current results for export
        self.current_results = []
        
        self.colors = {
            'bg': '#1e1e2e',
            'surface': '#2d2d3f',
            'primary': '#89b4fa',
            'success': '#a6e3a1',
            'error': '#f38ba8',
            'text': '#cdd6f4',
            'text_secondary': '#9399b2',
        }
        
        self.glossary_path = None
        self.text_path = None
        
        self._create_widgets()
        self._apply_styles()
    
    def _apply_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("Treeview",
                        background=self.colors['surface'],
                        foreground=self.colors['text'],
                        fieldbackground=self.colors['surface'],
                        borderwidth=0,
                        font=('Segoe UI', 10))
        style.configure("Treeview.Heading",
                        background=self.colors['bg'],
                        foreground=self.colors['primary'],
                        borderwidth=0,
                        font=('Segoe UI', 10, 'bold'))
        style.map('Treeview', background=[('selected', self.colors['primary'])])
        
        style.configure("TProgressbar",
                        background=self.colors['primary'],
                        troughcolor=self.colors['surface'],
                        thickness=6)
    
    def _create_widgets(self):
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Title
        tk.Label(main_frame, text="Glossary Compliance Checker",
                font=('Segoe UI', 18, 'bold'),
                bg=self.colors['bg'], fg=self.colors['primary']).pack(pady=(0, 5))
        tk.Label(main_frame, text="Ensure all glossary terms appear in your translations",
                font=('Segoe UI', 10), bg=self.colors['bg'],
                fg=self.colors['text_secondary']).pack(pady=(0, 30))
        
        # File selection
        cards_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        cards_frame.pack(fill=tk.X, pady=(0, 20))
        
        self._create_file_card(cards_frame, "Glossary (Excel)", "📖",
                              lambda: self._select_file('glossary'), 'glossary')
        self._create_file_card(cards_frame, "Translation File", "🌐",
                              lambda: self._select_file('text'), 'text')
        
        # Control buttons
        btn_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        btn_frame.pack(pady=(0, 20))
        
        self.run_btn = tk.Button(btn_frame, text="▶ RUN COMPLIANCE CHECK",
                                command=self._run_check, bg=self.colors['primary'],
                                fg=self.colors['bg'], font=('Segoe UI', 11, 'bold'),
                                padx=20, pady=8, cursor='hand2', relief=tk.FLAT,
                                state='disabled')
        self.run_btn.pack(side=tk.LEFT, padx=5)
        
        self.export_btn = tk.Button(btn_frame, text="📎 EXPORT TO EXCEL",
                                   command=self._export_results, bg=self.colors['surface'],
                                   fg=self.colors['text'], font=('Segoe UI', 10),
                                   padx=15, pady=8, cursor='hand2', relief=tk.FLAT,
                                   state='disabled')
        self.export_btn.pack(side=tk.LEFT, padx=5)
        
        # Progress
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 20))
        self.progress.pack_forget()
        
        # Results text area
        results_header = tk.Frame(main_frame, bg=self.colors['bg'])
        results_header.pack(fill=tk.X, pady=(0, 10))
        tk.Label(results_header, text="Results", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['bg'], fg=self.colors['text']).pack(side=tk.LEFT)
        
        # Text widget with scrollbar for copyable, wrappable results
        results_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        self.results_text = tk.Text(results_frame,
                                    bg=self.colors['surface'],
                                    fg=self.colors['text'],
                                    font=('Segoe UI', 10),
                                    wrap=tk.WORD,
                                    height=14,
                                    insertbackground=self.colors['text'])
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready", font=('Segoe UI', 9),
                                   bg=self.colors['surface'], fg=self.colors['text_secondary'],
                                   anchor='w', padx=10)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _create_file_card(self, parent, title, icon, command, card_id):
        card = tk.Frame(parent, bg=self.colors['surface'])
        card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        inner = tk.Frame(card, bg=self.colors['surface'])
        inner.pack(padx=15, pady=15, fill=tk.BOTH, expand=True)
        
        tk.Label(inner, text=icon, font=('Segoe UI', 24),
                bg=self.colors['surface'], fg=self.colors['primary']).pack(anchor='w')
        tk.Label(inner, text=title, font=('Segoe UI', 10, 'bold'),
                bg=self.colors['surface'], fg=self.colors['text']).pack(anchor='w', pady=(5, 5))
        
        label = tk.Label(inner, text="No file selected", font=('Segoe UI', 9),
                        fg=self.colors['text_secondary'], bg=self.colors['surface'])
        label.pack(anchor='w', pady=(0, 5))
        
        if card_id == 'glossary':
            self.glossary_label = label
        else:
            self.text_label = label
        
        tk.Button(inner, text="Browse...", command=command, bg=self.colors['primary'],
                 fg=self.colors['bg'], font=('Segoe UI', 9), padx=10, pady=3,
                 cursor='hand2', relief=tk.FLAT).pack(anchor='w')
        
        # Add convert button for translation files
        if card_id == 'text':
            tk.Button(inner, text="Convert to Excel", command=self._convert_to_excel,
                 bg=self.colors['bg'], fg=self.colors['primary'],
                 font=('Segoe UI', 8), padx=10, pady=2,
                 cursor='hand2', relief=tk.RAISED, bd=1).pack(anchor='w', pady=(5, 0))
    
    def _select_file(self, file_type):
        if file_type == 'glossary':
            filetypes = [("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        else:
            filetypes = [
                ("All supported", "*.xlsx *.xls *.sdlxliff"),
                ("Excel files", "*.xlsx *.xls"),
                ("SDLXLIFF files", "*.sdlxliff"),
                ("All files", "*.*")
            ]
        
        file_path = filedialog.askopenfilename(
            title=f"Select {file_type} file",
            filetypes=filetypes
        )
        if file_path:
            path = Path(file_path)
            if file_type == 'glossary':
                self.glossary_path = path
                self.glossary_label.config(text=path.name, fg=self.colors['success'])
            else:
                self.text_path = path
                self.text_label.config(text=path.name, fg=self.colors['success'])
            
            if self.glossary_path and self.text_path:
                self.run_btn.config(state='normal', bg=self.colors['success'])
                self.status_bar.config(text="✓ Ready to check")
    
    def _convert_to_excel(self):
        """Convert selected .sdlxliff file to Excel."""
        if not self.text_path:
            messagebox.showwarning("No File", "Please select a translation file first.")
            return
        
        if self.text_path.suffix.lower() != '.sdlxliff':
            messagebox.showinfo("Not SDLXLIFF", "Conversion is only available for .sdlxliff files.")
            return
        
        output_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile=self.text_path.stem + "_aligned.xlsx"
        )
        
        if output_path:
            try:
                from .exporters import convert_sdlxliff_to_xlsx
                result_path = convert_sdlxliff_to_xlsx(self.text_path, Path(output_path))
                messagebox.showinfo("Conversion Complete", f"File converted to:\n{result_path}")
            except Exception as e:
                messagebox.showerror("Conversion Failed", str(e))
    
    def _run_check(self):
        if not self.glossary_path or not self.text_path:
            return
        
        self.results_text.delete('1.0', tk.END)
        
        self.run_btn.config(state='disabled')
        self.export_btn.config(state='disabled')
        self.progress.pack(fill=tk.X, pady=(0, 20))
        self.progress.start()
        self.status_bar.config(text="Checking... Please wait")
        
        def task():
            try:
                checker = GlossaryChecker(self.glossary_path)
                self.current_results = checker.check_file(self.text_path)
                self.root.after(0, self._display_results)
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda msg=error_msg: self._show_error(msg))
            finally:
                self.root.after(0, self._stop_progress)
        
        threading.Thread(target=task, daemon=True).start()
    
    def _display_results(self):
        self.results_text.delete('1.0', tk.END)
        
        if not self.current_results:
            self.results_text.insert('1.0', "✓ No missing glossary terms found! All glossary terms present.\n")
            self.status_bar.config(text="✓ No missing glossary terms found!")
        else:
            for item in self.current_results:
                line = (f"Seg {item['segment_id']}: "
                       f"Missing '{item['english_term']}' → "
                       f"Expected: {', '.join(item['expected_spanish'])}\n"
                       f"  EN: {item['english_context']}\n"
                       f"  ES: {item['spanish_context']}\n\n")
                self.results_text.insert(tk.END, line)
            
            summary = export_summary_text(self.current_results)
            self.status_bar.config(text=summary.split('\n')[0])
            self.export_btn.config(state='normal')
    
    def _export_results(self):
        if not self.current_results:
            messagebox.showinfo("No Results", "No results to export. Run a check first.")
            return
        
        output_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")],
            initialfile="glossary_report.xlsx"
        )
        
        if output_path:
            try:
                export_to_excel(self.current_results, Path(output_path))
                messagebox.showinfo("Export Complete", f"Report saved to:\n{output_path}")
            except Exception as e:
                messagebox.showerror("Export Failed", str(e))
    
    def _show_error(self, error_msg):
        messagebox.showerror("Error", f"Failed to check file:\n{error_msg}")
        self.status_bar.config(text="Error occurred")
    
    def _stop_progress(self):
        self.progress.stop()
        self.progress.pack_forget()
        if self.glossary_path and self.text_path:
            self.run_btn.config(state='normal', bg=self.colors['primary'])
    
    def run(self):
        self.root.mainloop()


def main():
    app = GlossaryCheckerGUI()
    app.run()


if __name__ == '__main__':
    main()
