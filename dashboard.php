<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard</title>
    <link rel="stylesheet" href="style.css">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
        }

        .container {
            max-width: 1200px;
            margin: 20px auto;
            padding: 20px;
            background-color: #fff;
            border: 1px solid #ddd;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }

        h2 {
            text-align: center;
            color: #B73D3D; /* Brick red color */
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        th, td {
            padding: 12px;
            border-bottom: 1px solid #ddd;
            text-align: left;
        }

        th {
            background-color: #B73D3D; /* Brick red color */
            color: #fff;
        }

        tr:hover {
            background-color: #f5f5f5;
        }

        .user-image {
            width: 50px; /* Adjust as needed */
            height: 50px; /* Adjust as needed */
            object-fit: cover;
            border-radius: 50%;
        }

        .user-image-container {
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>User Dashboard</h2>
        <table id="student-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Image</th>
                    <th>First Name</th>
                    <th>Last Name</th>
                    <th>Middle Name</th>
                    <th>Level</th>
                </tr>
            </thead>
            <tbody>
                <!-- Student data will be inserted here -->

                <?php 
                include('./php/fetch_students.php')
                ?>
            </tbody>
        </table>
    </div>

    <script>
        // Function to fetch student data and populate the table
        function loadStudentData() {
            fetch('php/fetch_students.php')
                .then(response => response.json())
                .then(data => {
                    const tableBody = document.querySelector('#student-table tbody');
                    tableBody.innerHTML = '';

                    data.forEach(student => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${student.id}</td>
                            <td class="user-image-container">
                                <img src="${student.picture_path}" alt="${student.first_name} ${student.last_name}" class="user-image">
                            </td>
                            <td>${student.first_name}</td>
                            <td>${student.last_name}</td>
                            <td>${student.middle_name || 'N/A'}</td>
                            <td>${student.level}</td>
                        `;
                        tableBody.appendChild(row);
                    });
                })
                .catch(error => console.error('Error fetching student data:', error));
        }

        // Load student data on page load
        document.addEventListener('DOMContentLoaded', loadStudentData);
    </script>
</body>
</html>
