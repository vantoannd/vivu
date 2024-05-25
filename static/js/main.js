// fetch('/api/locations')
//             .then(response => response.json())
//             .then(data => {
//                 data.forEach(location => {
//                     var marker = L.marker([location.latitude, location.longitude]).addTo(map);
//                     marker.bindPopup(`<b>${location.name}</b><br>${location.description}<br><img src="${location.image_url}" width="100"><br>Rating: ${location.rating}`);
                    
//                     var listItem = document.createElement('li');
//                     listItem.textContent = location.name;
//                     var deleteButton = document.createElement('button');
//                     deleteButton.textContent = 'Xóa';
//                     deleteButton.addEventListener('click', function() {
//                         deleteLocation(location.id);
//                     });
//                     listItem.appendChild(deleteButton);
//                     document.getElementById('locationsList').appendChild(listItem);
//                 });
//             });

//         function deleteLocation(locationId) {
//             fetch(`/api/location/${locationId}`, {
//                 method: 'DELETE'
//             })
//             .then(response => {
//                 if (response.ok) {
//                     alert('Đã xóa địa điểm thành công!');
//                     location.reload();
//                 } else {
//                     alert('Đã xảy ra lỗi khi xóa địa điểm.');
//                 }
//             })
//             .catch(error => {
//                 console.error('Error:', error);
//             });
//         }
