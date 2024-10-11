'use strict';

function modalShownBook(event) {
  let button = event.relatedTarget;
  let bookId = button.getAttribute('data-book-id');
  let bookName = button.getAttribute('data-book-name');
  let newUrl = `/books/${bookId}/delete_book`;
  let form = document.getElementById('deleteModalBookForm');
  form.action = newUrl;
  document.getElementById('bookName').textContent = bookName;
}

document.addEventListener('DOMContentLoaded', function() {
  let deleteModalBook = document.getElementById('deleteModalBook');
  deleteModalBook.addEventListener('shown.bs.modal', modalShownBook);
});
