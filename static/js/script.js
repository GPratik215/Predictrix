function fetchData() {
    fetch('/fetch_data')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }

            const tableBody = document.querySelector("#user-table tbody");
            tableBody.innerHTML = "";  // Clear any existing rows

            data.results.forEach(user => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${user.userId}</td>
                    <td>${user.page}</td>
                    <td>${user.location}</td>
                    <td>${user.event}</td>
                    <td>${user.device}</td>
                `;
                tableBody.appendChild(row);
            });
        })
        .catch(error => {
            alert("Error fetching data from the backend");
            console.error(error);
        });
}

