/* Create Note Popup Code*/
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

function createNote() {
  const popupContainer = document.getElementById("popupContainer");
  const noteEditor = document.getElementById("note-editor");
  const noteTitle = document.getElementById("note-title");
  const noteContent = noteEditor.innerHTML.trim();
  const titleContent = noteTitle.value.trim();

  if (noteContent !== "" && titleContent !== "") {
      const note = {
          id: new Date().getTime(),
          title: titleContent,
          text: noteContent,
      };

      const existingNotes = JSON.parse(localStorage.getItem("notes")) || [];
      existingNotes.push(note);

      localStorage.setItem("notes", JSON.stringify(existingNotes));

      popupContainer.remove();
      displayNotes();
  }
}
  /* Display Notes Code*/
  
  function displayNotes() {
    const notesList = document.getElementById("notes-list");
    notesList.innerHTML = "";
  
    const notes = JSON.parse(localStorage.getItem("notes")) || [];
  
    notes.forEach((note) => {
      const listItem = document.createElement("li");
      listItem.className = "note-item";
      listItem.innerHTML = `
        <div class="note-header">${note.title}</div>
        <div class="note-content" contenteditable="false">${note.text}</div>
        <div id="noteBtns-container">
          <button id="editBtn" onclick="editNote(${note.id})">
            <i class="fa-solid fa-pen"></i>
          </button>
          <button id="deleteBtn" onclick="deleteNote(${note.id})">
            <i class="fa-solid fa-trash"></i>
          </button>
        </div>
      `;
      notesList.appendChild(listItem);
    });
  }
  
  /* Edit Note Popup Code*/
  
  function editNote(noteId) {
    const notes = JSON.parse(localStorage.getItem("notes")) || [];
    const noteToEdit = notes.find((note) => note.id == noteId);
    const noteText = noteToEdit ? noteToEdit.text : "";
    const noteTitle = noteToEdit ? noteToEdit.title : "";
  
    const editingPopup = document.createElement("div");
    editingPopup.innerHTML = `
      <div id="editing-container" data-note-id="${noteId}">
        <h1>Edit Note</h1>
        <input type="text" id="note-title" value="${noteTitle}" />
        <div id="format-bar">
          <button onclick="formatText('bold')"><i class="fa-solid fa-bold"></i></button>
          <button onclick="formatText('italic')"><i class="fa-solid fa-italic"></i></button>
          <button onclick="formatText2('insertBulletPoint')"><i class="fa-solid fa-circle"></i></button>
          <button onclick="formatText('insertCheckbox')"><i class="fa-solid fa-square-check"></i></button>
        </div>
        <div id="note-editor" contenteditable="true">${noteText}</div>
        <div id="btn-container">
          <button id="submitBtn" onclick="updateNote()">Done</button>
          <button id="closeBtn" onclick="closeEditPopup()">Cancel</button>
        </div>
      </div>
    `;
    document.body.appendChild(editingPopup);
  }
  
  function closeEditPopup() {
    const editingPopup = document.getElementById("editing-container");
  
    if (editingPopup) {
      editingPopup.remove();
    }
  }
  
  function updateNote() {
    const noteEditor = document.getElementById("note-editor");
    const noteTitle = document.getElementById("note-title");
    const noteContent = noteEditor.innerHTML.trim();
    const titleContent = noteTitle.value.trim();
    const editingPopup = document.getElementById("editing-container");
  
    if (noteContent !== "" && titleContent !== "") {
      const noteId = editingPopup.getAttribute("data-note-id");
      let notes = JSON.parse(localStorage.getItem("notes")) || [];
  
      const updatedNotes = notes.map((note) => {
        if (note.id == noteId) {
          return { id: note.id, title: titleContent, text: noteContent };
        }
        return note;
      });
  
      localStorage.setItem("notes", JSON.stringify(updatedNotes));
  
      editingPopup.remove();
      displayNotes();
    }
  }
  
  /* Delete Note Logic*/
  
  function deleteNote(noteId) {
    let notes = JSON.parse(localStorage.getItem("notes")) || [];
    notes = notes.filter((note) => note.id !== noteId);
  
    localStorage.setItem("notes", JSON.stringify(notes));
    displayNotes();
  }
  
  displayNotes();