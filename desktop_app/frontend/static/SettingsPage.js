const editBtn = document.getElementById('editBtn');
const profileForm = document.getElementById('profileForm');
let editMode = false;
 
editBtn.addEventListener('click', () => {
    editMode = !editMode;
    const inputs = profileForm.querySelectorAll('input');
    inputs.forEach(input => input.disabled = !editMode);
 
    editBtn.textContent = editMode ? 'Save' : 'Edit';
});
 
const addEmailBtn = document.getElementById('addEmailBtn');
const emailList = document.getElementById('emailList');
 
addEmailBtn.addEventListener('click', () => {
    const newEmail = prompt("Enter new email address:");
    if (newEmail) {
        const p = document.createElement('p');
        p.innerHTML = `<i class="bi bi-envelope me-2"></i> ${newEmail} <small class="text-muted">just now</small>`;
        emailList.appendChild(p);
    }
});
 