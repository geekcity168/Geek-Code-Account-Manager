document.querySelectorAll('.dropdown-item').forEach(item => {
    item.addEventListener('click', function (e) {
        e.preventDefault(); // prevent anchor default behavior
        const sortType = this.getAttribute('data-sort');
        document.querySelector('.sort').innerHTML = sortType;
    });
});

function showLoader() {
    document.getElementById('overlay').style.display = 'flex';
    
  }
  
// Hide the loading overlay
function hideLoader() {
    document.getElementById('overlay').style.display = 'none';
}


document.getElementById("refreshBtn").addEventListener("click", function() {
    showLoader();
    document.getElementById("spinner").style.display = "block";
    document.getElementById("successIcon").style.display = "none";
    document.getElementById("status").innerText = "Loading...";

    setTimeout(() => {
        document.getElementById("spinner").style.display = "none";
        document.getElementById("successIcon").style.display = "block";
        document.getElementById("status").innerText = "Refresh successful";
        setTimeout(() => {
            location.reload();
        }, 3000);
    }, 3000);
});

const token = localStorage.getItem('authToken');

fetch('http://localhost:5000/api/user-data', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({})
})
.then(response => response.json())
.then(data => {
    document.getElementById("userName").textContent = data.name;
    document.getElementById("email").textContent = data.email;
    document.getElementById("phoneNumber").textContent = data.phone;
})
.catch(error => console.error('Error:', error));



