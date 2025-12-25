// chat/static/chat/js/chat.js

function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function updateMessageCount(count) {
  const badge = document.getElementById("message-count");
  if (badge) badge.textContent = String(count);
}

function scrollToBottom() {
  const container = document.getElementById("chat-messages");
  if (container) {
    container.scrollTop = container.scrollHeight;
  }
}

function createMessageElement(message) {
  const div = document.createElement("div");
  div.className = "chat-message";
  div.dataset.messageId = message.id;

  if (message.is_highlighted) {
    div.classList.add("highlighted");
  }

  const safeName = escapeHtml(message.display_name || message.user);
  const safeTime = escapeHtml(message.created_at);
  const safeText = escapeHtml(message.message);

  const deleteBtn = message.can_delete
    ? `<button class="btn btn-sm btn-outline-danger delete-message" type="button">Eliminar</button>`
    : "";

  div.innerHTML = `
    <div class="message-header">
      <strong>${safeName}</strong>
      <small class="text-muted">${safeTime}</small>
    </div>
    <div class="message-content">${safeText}</div>
    <div class="message-actions">${deleteBtn}</div>
  `;

  return div;
}

async function loadMessages() {
  const messagesContainer = document.getElementById("chat-messages");
  const errorsContainer = document.getElementById("chat-errors");
  if (!messagesContainer) return;

  try {
    const res = await fetch(`/chat/${eventId}/messages/`, {
      headers: { "X-Requested-With": "XMLHttpRequest" },
    });
    const data = await res.json();

    messagesContainer.innerHTML = "";
    const msgs = data.messages || [];

    msgs.forEach((m) => {
      messagesContainer.appendChild(createMessageElement(m));
    });

    updateMessageCount(msgs.length);
    scrollToBottom();

    if (errorsContainer) errorsContainer.textContent = "";
  } catch (err) {
    if (errorsContainer) errorsContainer.textContent = "Error carregant missatges.";
  }
}

function getCsrfToken() {
  // Agafem el token del input hidden del form
  const input = document.querySelector('#chat-form input[name="csrfmiddlewaretoken"]');
  return input ? input.value : "";
}

function showErrors(errors) {
  const errorsContainer = document.getElementById("chat-errors");
  if (!errorsContainer) return;

  if (!errors) {
    errorsContainer.textContent = "";
    return;
  }

  // errors pot ser: {message:[...]} o {"__all__":[...]}
  const msgs = [];
  for (const key in errors) {
    if (Array.isArray(errors[key])) {
      errors[key].forEach((e) => msgs.push(e));
    }
  }

  errorsContainer.textContent = msgs.join(" ");
}

async function sendMessage(e) {
  e.preventDefault();

  const form = document.getElementById("chat-form");
  if (!form) return;

  const textarea = form.querySelector("textarea");
  const message = textarea ? textarea.value : "";

  const csrfToken = getCsrfToken();

  try {
    const res = await fetch(`/chat/${eventId}/send/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": csrfToken,
        "X-Requested-With": "XMLHttpRequest",
      },
      body: new URLSearchParams({ message }),
    });

    const data = await res.json();

    if (data.success) {
      if (textarea) textarea.value = "";
      showErrors(null);
      await loadMessages();
    } else {
      showErrors(data.errors);
    }
  } catch (err) {
    showErrors({ "__all__": ["Error enviant el missatge."] });
  }
}

async function deleteMessage(messageId) {
  const csrfToken = getCsrfToken();

  try {
    const res = await fetch(`/chat/message/${messageId}/delete/`, {
      method: "POST",
      headers: {
        "X-CSRFToken": csrfToken,
        "X-Requested-With": "XMLHttpRequest",
      },
    });

    const data = await res.json();
    if (data.success) {
      await loadMessages();
    } else {
      showErrors({ "__all__": [data.error || "No s'ha pogut eliminar."] });
    }
  } catch (err) {
    showErrors({ "__all__": ["Error eliminant el missatge."] });
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("chat-form");
  const messagesContainer = document.getElementById("chat-messages");

  if (form) {
    form.addEventListener("submit", sendMessage);
  }

  if (messagesContainer) {
    // Event delegation per botons eliminar
    messagesContainer.addEventListener("click", (e) => {
      const btn = e.target.closest(".delete-message");
      if (!btn) return;

      const msgDiv = e.target.closest(".chat-message");
      const messageId = msgDiv ? msgDiv.dataset.messageId : null;
      if (!messageId) return;

      if (confirm("Vols eliminar aquest missatge?")) {
        deleteMessage(messageId);
      }
    });
  }

  // Carrega inicial i polling cada 3 segons
  loadMessages();
  setInterval(loadMessages, 3000);
});
