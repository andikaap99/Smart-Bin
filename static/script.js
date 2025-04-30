const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const captureBtn = document.getElementById('captureBtn');
const cameraForm = document.getElementById('cameraForm');
const imageInput = document.getElementById('imageFromCamera');

// Cek apakah semua elemen ditemukan
console.log("video element:", video);
console.log("canvas element:", canvas);
console.log("capture button:", captureBtn);
console.log("form element:", cameraForm);
console.log("image input:", imageInput);

// Jalankan kamera saat halaman dimuat
window.onload = () => {
  console.log("Window loaded, requesting camera...");
  navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
      video.srcObject = stream;
      console.log("Camera stream started.");
    })
    .catch(err => {
      console.error('Camera not accessible:', err);
      alert('Camera not accessible: ' + err.message);
    });
};

captureBtn.addEventListener('click', () => {
  console.log("Capture button clicked.");
  const context = canvas.getContext('2d');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  context.drawImage(video, 0, 0);

  console.log("Image drawn on canvas.");

  canvas.toBlob(blob => {
    console.log("Canvas converted to blob.");

    const file = new File([blob], 'capture.jpg', { type: 'image/jpeg' });

    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    imageInput.files = dataTransfer.files;

    console.log("Blob added to input[type=file].");

    // Tampilkan form untuk submit
    cameraForm.classList.remove('hidden');
    console.log("Form is now visible.");
  }, 'image/jpeg');
});
