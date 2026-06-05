from __future__ import annotations

import queue
import threading
import tkinter as tk
from collections.abc import Callable
from tkinter import ttk
from typing import Any, cast

from .mail import EmailClientError, fetch_messages, send_email
from .models import (
    Credentials,
    InboxMessage,
    OutgoingMessage,
    POP3Settings,
    SecurityMode,
    SMTPSettings,
)

SECURITY_CHOICES = ("ssl", "starttls", "none")


class EmailApp(tk.Tk):
    def __init__(self, start_tab: str = "send") -> None:
        super().__init__()
        self.title("SMTP and POP3 Email Client")
        self.geometry("980x700")
        self.minsize(820, 600)

        self._task_queue: queue.Queue[tuple[Callable[[Any], None] | None, Any, str | None]] = (
            queue.Queue()
        )
        self._busy_controls: list[ttk.Button] = []
        self._messages: list[InboxMessage] = []

        self._build_variables()
        self._configure_styles()
        self._build_layout(start_tab)
        self.after(100, self._poll_tasks)

    def _build_variables(self) -> None:
        self.email_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.show_password_var = tk.BooleanVar(value=False)

        self.smtp_host_var = tk.StringVar(value="smtp.gmail.com")
        self.smtp_port_var = tk.StringVar(value="587")
        self.smtp_security_var = tk.StringVar(value="starttls")
        self.to_var = tk.StringVar()
        self.subject_var = tk.StringVar()

        self.pop_host_var = tk.StringVar(value="pop.gmail.com")
        self.pop_port_var = tk.StringVar(value="995")
        self.pop_security_var = tk.StringVar(value="ssl")
        self.limit_var = tk.StringVar(value="10")

        self.status_var = tk.StringVar(value="Ready")

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        style.configure("Title.TLabel", font=("Helvetica", 16, "bold"))
        style.configure("Section.TLabelframe.Label", font=("Helvetica", 11, "bold"))
        style.configure("Status.TLabel", padding=(10, 6))
        style.configure("Success.Status.TLabel", foreground="#16703c")
        style.configure("Error.Status.TLabel", foreground="#a52323")
        style.configure("Muted.TLabel", foreground="#555")

    def _build_layout(self, start_tab: str) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        account = ttk.LabelFrame(self, text="Account", style="Section.TLabelframe")
        account.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 8))
        account.columnconfigure(1, weight=1)
        account.columnconfigure(3, weight=1)

        ttk.Label(account, text="Email").grid(row=0, column=0, sticky="w", padx=(12, 6), pady=10)
        ttk.Entry(account, textvariable=self.email_var).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(0, 12),
            pady=10,
        )
        ttk.Label(account, text="App password").grid(
            row=0,
            column=2,
            sticky="w",
            padx=(0, 6),
            pady=10,
        )
        self.password_entry = ttk.Entry(account, textvariable=self.password_var, show="*")
        self.password_entry.grid(row=0, column=3, sticky="ew", padx=(0, 12), pady=10)
        ttk.Checkbutton(
            account,
            text="Show",
            variable=self.show_password_var,
            command=self._toggle_password,
        ).grid(row=0, column=4, sticky="w", padx=(0, 12), pady=10)

        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=14, pady=8)

        self.send_tab = ttk.Frame(self.notebook, padding=12)
        self.inbox_tab = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(self.send_tab, text="Send")
        self.notebook.add(self.inbox_tab, text="Inbox")
        self._build_send_tab()
        self._build_inbox_tab()

        if start_tab == "inbox":
            self.notebook.select(self.inbox_tab)

        self.status_label = ttk.Label(self, textvariable=self.status_var, style="Status.TLabel")
        self.status_label.grid(row=2, column=0, sticky="ew")

    def _build_send_tab(self) -> None:
        self.send_tab.columnconfigure(0, weight=1)
        self.send_tab.rowconfigure(2, weight=1)

        server = ttk.LabelFrame(self.send_tab, text="SMTP Server", style="Section.TLabelframe")
        server.grid(row=0, column=0, sticky="ew")
        for column in (1, 3, 5):
            server.columnconfigure(column, weight=1)
        self._server_fields(
            server,
            host_var=self.smtp_host_var,
            port_var=self.smtp_port_var,
            security_var=self.smtp_security_var,
        )

        fields = ttk.LabelFrame(self.send_tab, text="Message", style="Section.TLabelframe")
        fields.grid(row=1, column=0, sticky="ew", pady=(12, 8))
        fields.columnconfigure(1, weight=1)
        ttk.Label(fields, text="To").grid(row=0, column=0, sticky="w", padx=(12, 6), pady=(10, 6))
        ttk.Entry(fields, textvariable=self.to_var).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(0, 12),
            pady=(10, 6),
        )
        ttk.Label(fields, text="Subject").grid(
            row=1,
            column=0,
            sticky="w",
            padx=(12, 6),
            pady=(0, 10),
        )
        ttk.Entry(fields, textvariable=self.subject_var).grid(
            row=1,
            column=1,
            sticky="ew",
            padx=(0, 12),
            pady=(0, 10),
        )

        body_frame = ttk.LabelFrame(self.send_tab, text="Body", style="Section.TLabelframe")
        body_frame.grid(row=2, column=0, sticky="nsew")
        body_frame.columnconfigure(0, weight=1)
        body_frame.rowconfigure(0, weight=1)
        self.body_text = tk.Text(body_frame, wrap="word", undo=True, height=14)
        body_scroll = ttk.Scrollbar(body_frame, orient="vertical", command=self.body_text.yview)
        self.body_text.configure(yscrollcommand=body_scroll.set)
        self.body_text.grid(row=0, column=0, sticky="nsew", padx=(12, 0), pady=12)
        body_scroll.grid(row=0, column=1, sticky="ns", padx=(0, 12), pady=12)

        actions = ttk.Frame(self.send_tab)
        actions.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        actions.columnconfigure(0, weight=1)
        ttk.Button(actions, text="Clear", command=self._clear_message_form).grid(
            row=0,
            column=1,
            sticky="e",
            padx=(0, 8),
        )
        self.send_button = ttk.Button(actions, text="Send Email", command=self._send_clicked)
        self.send_button.grid(row=0, column=2, sticky="e")
        self._busy_controls.append(self.send_button)

    def _build_inbox_tab(self) -> None:
        self.inbox_tab.columnconfigure(0, weight=1)
        self.inbox_tab.rowconfigure(1, weight=1)
        self.inbox_tab.rowconfigure(2, weight=1)

        server = ttk.LabelFrame(self.inbox_tab, text="POP3 Server", style="Section.TLabelframe")
        server.grid(row=0, column=0, sticky="ew")
        for column in (1, 3, 5, 7):
            server.columnconfigure(column, weight=1)
        self._server_fields(
            server,
            host_var=self.pop_host_var,
            port_var=self.pop_port_var,
            security_var=self.pop_security_var,
        )
        ttk.Label(server, text="Limit").grid(row=0, column=6, sticky="w", padx=(10, 6), pady=10)
        ttk.Spinbox(server, from_=1, to=100, textvariable=self.limit_var, width=6).grid(
            row=0,
            column=7,
            sticky="ew",
            padx=(0, 12),
            pady=10,
        )

        columns = ("number", "sender", "subject", "date")
        self.message_list = ttk.Treeview(
            self.inbox_tab,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=10,
        )
        self.message_list.heading("number", text="#")
        self.message_list.heading("sender", text="From")
        self.message_list.heading("subject", text="Subject")
        self.message_list.heading("date", text="Date")
        self.message_list.column("number", width=60, stretch=False, anchor="center")
        self.message_list.column("sender", width=220, stretch=True)
        self.message_list.column("subject", width=320, stretch=True)
        self.message_list.column("date", width=220, stretch=True)
        self.message_list.bind("<<TreeviewSelect>>", self._message_selected)
        list_scroll = ttk.Scrollbar(
            self.inbox_tab,
            orient="vertical",
            command=self.message_list.yview,
        )
        self.message_list.configure(yscrollcommand=list_scroll.set)
        self.message_list.grid(row=1, column=0, sticky="nsew", pady=(12, 8))
        list_scroll.grid(row=1, column=1, sticky="ns", pady=(12, 8))

        preview_frame = ttk.LabelFrame(self.inbox_tab, text="Preview", style="Section.TLabelframe")
        preview_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        self.preview_text = tk.Text(preview_frame, wrap="word", state="disabled", height=10)
        preview_scroll = ttk.Scrollbar(
            preview_frame,
            orient="vertical",
            command=self.preview_text.yview,
        )
        self.preview_text.configure(yscrollcommand=preview_scroll.set)
        self.preview_text.grid(row=0, column=0, sticky="nsew", padx=(12, 0), pady=12)
        preview_scroll.grid(row=0, column=1, sticky="ns", padx=(0, 12), pady=12)

        actions = ttk.Frame(self.inbox_tab)
        actions.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        actions.columnconfigure(0, weight=1)
        ttk.Label(
            actions,
            text="Latest messages are shown first.",
            style="Muted.TLabel",
        ).grid(row=0, column=0, sticky="w")
        self.fetch_button = ttk.Button(actions, text="Fetch Mail", command=self._fetch_clicked)
        self.fetch_button.grid(row=0, column=1, sticky="e")
        self._busy_controls.append(self.fetch_button)

    def _server_fields(
        self,
        parent: ttk.LabelFrame,
        host_var: tk.StringVar,
        port_var: tk.StringVar,
        security_var: tk.StringVar,
    ) -> None:
        ttk.Label(parent, text="Host").grid(row=0, column=0, sticky="w", padx=(12, 6), pady=10)
        ttk.Entry(parent, textvariable=host_var).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(0, 10),
            pady=10,
        )
        ttk.Label(parent, text="Port").grid(row=0, column=2, sticky="w", padx=(0, 6), pady=10)
        ttk.Entry(parent, textvariable=port_var, width=8).grid(
            row=0,
            column=3,
            sticky="ew",
            padx=(0, 10),
            pady=10,
        )
        ttk.Label(parent, text="Security").grid(row=0, column=4, sticky="w", padx=(0, 6), pady=10)
        ttk.Combobox(
            parent,
            textvariable=security_var,
            values=SECURITY_CHOICES,
            state="readonly",
            width=10,
        ).grid(row=0, column=5, sticky="ew", padx=(0, 10), pady=10)

    def _toggle_password(self) -> None:
        self.password_entry.configure(show="" if self.show_password_var.get() else "*")

    def _send_clicked(self) -> None:
        try:
            credentials = self._credentials()
            settings = SMTPSettings(
                host=self._required(self.smtp_host_var, "SMTP host"),
                port=self._positive_int(self.smtp_port_var, "SMTP port"),
                security=self._security(self.smtp_security_var),
            )
            message = OutgoingMessage(
                sender=credentials.username,
                recipient=self._required(self.to_var, "Recipient"),
                subject=self._required(self.subject_var, "Subject"),
                body=self._body(),
            )
        except ValueError as exc:
            self._set_status(str(exc), error=True)
            return

        self._start_task(
            "Sending email...",
            lambda: send_email(settings, credentials, message),
            lambda _: self._set_status("Email sent.", success=True),
        )

    def _fetch_clicked(self) -> None:
        try:
            credentials = self._credentials()
            settings = POP3Settings(
                host=self._required(self.pop_host_var, "POP3 host"),
                port=self._positive_int(self.pop_port_var, "POP3 port"),
                security=self._security(self.pop_security_var),
            )
            limit = self._positive_int(self.limit_var, "Message limit")
        except ValueError as exc:
            self._set_status(str(exc), error=True)
            return

        self._start_task(
            "Fetching mail...",
            lambda: fetch_messages(settings, credentials, limit=limit),
            self._render_messages,
        )

    def _start_task(
        self,
        status: str,
        worker: Callable[[], Any],
        on_success: Callable[[Any], None],
    ) -> None:
        self._set_busy(True)
        self._set_status(status)

        def run() -> None:
            try:
                result = worker()
            except (EmailClientError, ValueError, OSError) as exc:
                self._task_queue.put((None, None, str(exc)))
            except Exception as exc:
                self._task_queue.put((None, None, f"Unexpected error: {exc}"))
            else:
                self._task_queue.put((on_success, result, None))

        threading.Thread(target=run, daemon=True).start()

    def _poll_tasks(self) -> None:
        while True:
            try:
                on_success, result, error = self._task_queue.get_nowait()
            except queue.Empty:
                break

            self._set_busy(False)
            if error is not None:
                self._set_status(error, error=True)
            elif on_success is not None:
                on_success(result)

        self.after(100, self._poll_tasks)

    def _set_busy(self, busy: bool) -> None:
        state = ["disabled"] if busy else ["!disabled"]
        for control in self._busy_controls:
            control.state(state)

    def _credentials(self) -> Credentials:
        return Credentials(
            username=self._required(self.email_var, "Email"),
            password=self._required(self.password_var, "App password"),
        )

    def _body(self) -> str:
        value = self.body_text.get("1.0", "end-1c").strip()
        if not value:
            raise ValueError("Body is required.")
        return value

    def _render_messages(self, messages: list[InboxMessage]) -> None:
        self._messages = messages
        for item in self.message_list.get_children():
            self.message_list.delete(item)

        for index, message in enumerate(messages):
            self.message_list.insert(
                "",
                "end",
                iid=str(index),
                values=(message.number, message.sender, message.subject, message.date),
            )

        self._set_preview("")
        count = len(messages)
        suffix = "message" if count == 1 else "messages"
        self._set_status(f"Fetched {count} {suffix}.", success=True)

    def _message_selected(self, event: tk.Event[ttk.Treeview]) -> None:
        selection = self.message_list.selection()
        if not selection:
            return
        index = int(selection[0])
        message = self._messages[index]
        header = f"From: {message.sender}\nSubject: {message.subject}\nDate: {message.date}\n\n"
        self._set_preview(header + message.body)

    def _set_preview(self, value: str) -> None:
        self.preview_text.configure(state="normal")
        self.preview_text.delete("1.0", "end")
        self.preview_text.insert("1.0", value)
        self.preview_text.configure(state="disabled")

    def _clear_message_form(self) -> None:
        self.to_var.set("")
        self.subject_var.set("")
        self.body_text.delete("1.0", "end")
        self._set_status("Ready")

    def _set_status(self, value: str, success: bool = False, error: bool = False) -> None:
        self.status_var.set(value)
        if success:
            self.status_label.configure(style="Success.Status.TLabel")
        elif error:
            self.status_label.configure(style="Error.Status.TLabel")
        else:
            self.status_label.configure(style="Status.TLabel")

    def _required(self, variable: tk.StringVar, label: str) -> str:
        value = variable.get().strip()
        if not value:
            raise ValueError(f"{label} is required.")
        return value

    def _positive_int(self, variable: tk.StringVar, label: str) -> int:
        value = self._required(variable, label)
        try:
            number = int(value)
        except ValueError as exc:
            raise ValueError(f"{label} must be a number.") from exc
        if number < 1:
            raise ValueError(f"{label} must be greater than zero.")
        return number

    def _security(self, variable: tk.StringVar) -> SecurityMode:
        value = variable.get().strip()
        if value not in SECURITY_CHOICES:
            raise ValueError("Security must be ssl, starttls, or none.")
        return cast(SecurityMode, value)
