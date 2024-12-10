function copyToClipboard(id) {
  const bibtexCode = document.getElementById(id).textContent;
  navigator.clipboard.writeText(bibtexCode).then(() => {
      alert('BibTeX copied to clipboard!');
  });
}