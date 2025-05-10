/* Create Note Popup Code */
function popup() {
  const popupContainer = document.createElement("div");
  popupContainer.innerHTML = `
    <div id="popupContainer">
      <h1>New Note</h1>
      <input type="text" id="note-title" placeholder="Enter Title..." />
      <div id="format-bar">
        <button onclick="formatText('bold')"><i class="fa-solid fa-bold"></i></button>
        <button onclick="formatText('italic')"><i class="fa-solid fa-italic"></i></button>
        <button onclick="formatText2('insertBulletPoint')"><i class="fa-solid fa-circle"></i></button>
        <button onclick="formatText('insertCheckbox')"><i class="fa-solid fa-square-check"></i></button>
      </div>
      <div id="note-editor" contenteditable="true" placeholder="Enter your note..."></div>
      <div id="btn-container">
        <button id="submitBtn" onclick="createNote()">Create Note</button>
        <button id="closeBtn" onclick="closePopup()">Close</button>
      </div>
    </div>
  `;
  document.body.appendChild(popupContainer);
}

function formatText(command) {
  if (command === "insertCheckbox") {
    document.execCommand("insertHTML", false, '<input type="checkbox"> ');
  } else {
    document.execCommand(command, false, null);
  }
}

function formatText2(command) {
  if (command === "insertBulletPoint") {
    document.execCommand("insertHTML", false, '•&nbsp;');
  } else {
    document.execCommand(command, false, null);
  }
}

function closePopup() {
  const popupContainer = document.getElementById("popupContainer");
  if (popupContainer) {
    popupContainer.remove();
  }
}

/* Create Note API */
function createNote() {
  const popupContainer = document.getElementById("popupContainer");
  const noteEditor = document.getElementById("note-editor");
  const noteTitle = document.getElementById("note-title");
  const noteContent = noteEditor.innerHTML.trim();
  const titleContent = noteTitle.value.trim();

  if (noteContent !== "" && titleContent !== "") {
    fetch('/api/notes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: titleContent, content: noteContent })
    })
      .then(response => response.json())
      .then(data => {
        console.log('Note created:', data);
        closePopup();
        displayNotes();
      })
      .catch(error => console.error('Error creating note:', error));

      const message = document.createElement("div");
      message.textContent = "Note Saved!";
      message.style.cssText = `
          position: fixed;
          top: 20px;
          left: 50%;
          transform: translateX(-50%);
          background-color:rgb(141, 69, 143);
          color: white;
          padding: 10px 20px;
          border-radius: 5px;
          z-index: 1000;
          opacity: 0;
          transition: opacity 0.5s ease-in-out;
          `;
          document.body.appendChild(message);

          setTimeout(() => {
            message.style.opacity = 1;
          }, 50);

          setTimeout(() => {
            message.style.opacity = 0;
            setTimeout(() => {
              message.remove();
            }, 500);
            }, 2000);
  }
}


/* Display Notes */
function displayNotes() {
  const notesList = document.getElementById("notes-list");
  if (!notesList) {
    console.error('No element with id="notes-list" found.');
    return;
  }

  notesList.innerHTML = "";

  fetch('/api/notes')
    .then(response => response.json())
    .then(notes => {
      notes.forEach(note => {
        const listItem = document.createElement("li");
        listItem.className = "note-item";
        listItem.innerHTML = `
          <div class="note-header">${note.title}</div>
          <div class="note-content" contenteditable="false">${note.content}</div>
          <div id="noteBtns-container">
            <button id="editBtn" onclick="editNote(${note.id})"><i class="fa-solid fa-pen"></i></button>
            <button id="deleteBtn" onclick="deleteNote(${note.id})"><i class="fa-solid fa-trash"></i></button>
            <button id="deleteBtn" onclick="shareNote(${note.id})"><i class="fa-solid fa-share-from-square"></i></button>

          </div>
        `;
        notesList.appendChild(listItem);
      });
    })
    .catch(error => console.error('Error fetching notes:', error));
}

/* Edit Note Popup */
function editNote(noteId) {
  fetch(`/api/notes`)
    .then(response => response.json())
    .then(notes => {
      const noteToEdit = notes.find(note => note.id === noteId);
      if (!noteToEdit) {
        console.error('Note not found.');
        return;
      }

      const editingPopup = document.createElement("div");
      editingPopup.innerHTML = `
        <div id="editing-container" data-note-id="${noteId}">
          <h1>Edit Note</h1>
          <input type="text" id="note-title" value="${noteToEdit.title}" />
          <div id="format-bar">
            <button onclick="formatText('bold')"><i class="fa-solid fa-bold"></i></button>
            <button onclick="formatText('italic')"><i class="fa-solid fa-italic"></i></button>
            <button onclick="formatText2('insertBulletPoint')"><i class="fa-solid fa-circle"></i></button>
            <button onclick="formatText('insertCheckbox')"><i class="fa-solid fa-square-check"></i></button>
          </div>
          <div id="note-editor" contenteditable="true">${noteToEdit.content}</div>
          <div id="btn-container">
            <button id="submitBtn" onclick="updateNote()">Done</button>
            <button id="closeBtn" onclick="closeEditPopup()">Cancel</button>
          </div>
        </div>
      `;
      document.body.appendChild(editingPopup);
    })
    .catch(error => console.error('Error loading note for editing:', error));
}

/* Update Note API */
function updateNote() {
  const noteEditor = document.getElementById("note-editor");
  const noteTitle = document.getElementById("note-title");
  const noteContent = noteEditor.innerHTML.trim();
  const titleContent = noteTitle.value.trim();
  const editingPopup = document.getElementById("editing-container");

  if (noteContent !== "" && titleContent !== "") {
    const noteId = editingPopup.getAttribute("data-note-id");

    fetch(`/api/notes/${noteId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: titleContent, content: noteContent })
    })
      .then(response => response.json())
      .then(data => {
        console.log('Note updated:', data);
        editingPopup.remove();
        displayNotes();
      })
      .catch(error => console.error('Error updating note:', error));
  }
}

/* Delete Note API */
function deleteNote(noteId) {
  fetch(`/api/notes/${noteId}`, {
    method: 'DELETE'
  })
    .then(response => response.json())
    .then(data => {
      console.log('Note deleted:', data);
      displayNotes();
    })
    .catch(error => console.error('Error deleting note:', error));
}

function shareNote(noteId) {
  fetch(`/api/notes/${noteId}`, {
    method: 'DELETE'
  })
    .then(response => response.json())
    .then(data => {
      console.log('Note deleted:', data);
      displayNotes();
    })
    .catch(error => console.error('Error deleting note:', error));
}

/* Close Edit Popup */
function closeEditPopup() {
  const editingPopup = document.getElementById("editing-container");
  if (editingPopup) {
    editingPopup.remove();
  }
}

/* Initialize Notes Display */
displayNotes();