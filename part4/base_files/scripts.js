/* 
  This is a SAMPLE FILE to get you started.
  Please, follow the project instructions to complete the tasks.
*/

document.addEventListener('DOMContentLoaded', () => {
    checkAuthentication();
    populatePriceFilter();
    const loginForm = document.getElementById('login-form');

    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            // Your code to handle form submission
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            loginUser(email, password);

        });
    }

});



async function loginUser(email, password) {
  const response = await fetch('http://127.0.0.1:5000/api/v1/login', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email, password })
  });
  
  // Handle the response
  if (response.ok) {
    const data = await response.json();
    // Adjust SameSite and Secure attributes for local testing
    // document.cookie = `token=${data.access_token}; path=/; SameSite=Lax`;
    document.cookie = `token=${data.access_token}; path=/; SameSite=None; Secure`;
    window.location.href = 'index.html';
  } else {
    alert('Login failed: ' + response.statusText);
  }
}


function getCookie(name) {
  // Function to get a cookie value by its name
  // Your code here
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2)
    return parts.pop().split(";").shift();
  return null;
}

function checkAuthentication() {
  const token = getCookie('token');
  const loginLink = document.getElementById('login-link');
  const addReviewSection = document.getElementById('add-review');

  if (!token) {
      if (loginLink)
        loginLink.style.display = 'block';
      if (addReviewSection)
        addReviewSection.style.display = 'none';
  } else {
      if (loginLink){
        loginLink.style.display = 'none';

        fetchPlaces(token);
      }

      if (addReviewSection){
        addReviewSection.style.display = 'block';

        const place_id = getPlaceIdFromURL();

        if (place_id) {
          // Store the token for later use
          fetchPlaceDetails(token, place_id);
        }
      }
}
}


    
async function fetchPlaces(token) {
  // Make a GET request to fetch places data
  // Include the token in the Authorization header
  // Handle the response and pass the data to displayPlaces function
  try {
    const response = await fetch("http://127.0.0.1:5000/api/v1/places", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error("Network response was not ok " + response.statusText);
    }

    const places = await response.json();
    console.log(places);
    displayPlaces(places);
  } catch (error) {
    console.error("Fetch error: ", error);
  }
}


function displayPlaces(places) {
  
  const placesList = document.getElementById("places-list");
  // Clear the current content of the places list
  placesList.innerHTML = "";
  
  // Iterate over the places data
    places.forEach((place) => {
    // For each place, create a div element and set its content
    const placeDiv = document.createElement("div");
    placeDiv.className = "place-card";
    placeDiv.setAttribute('data-price', place.price);
    placeDiv.innerHTML = `
            <img src="images/place1.jpg" alt="Place Image" class="place-image">
            <h2>${place.title}</h2>
            <p>Price per night: $${place.price}</p>
            <a class="details-button" href="place.html?place_id=${place.id}">View Details</button>
        `;
    // Append the created element to the places list
    placesList.appendChild(placeDiv);
  });

}

function filterPlacesByPrice(selectedPrice) {
  const places = document.querySelectorAll('.place-card');

  places.forEach(place => {
      const price = place.getAttribute('data-price');
      if (selectedPrice === 'All' || price === selectedPrice) {
          place.style.display = 'block';
      } else {
          place.style.display = 'none';
      }
  });
}


async function populatePriceFilter() {
  try {
    const response = await fetch("http://127.0.0.1:5000/api/v1/places");
    if (!response.ok) {
      throw new Error("Network response was not ok " + response.statusText);
    }

    const places = await response.json();

    const priceFilter = document.getElementById("price-filter");

    if (priceFilter) {
      // Collect unique price values
      const uniquePrices = new Set();

      places.forEach((place) => {
        // Normalize price to string for comparison
        const priceValue = String(place.price);
        uniquePrices.add(priceValue);
      });

      // Retain the "All" option
      const allOption = Array.from(priceFilter.options).find(
        (option) => option.value === "All"
      );

      // Clear all options
      priceFilter.innerHTML = ""; // Clear all options but retain "All"

      if (allOption) {
        priceFilter.appendChild(allOption); // Add "All" back at the top
      }

      // Sort prices in descending order and append them
      Array.from(uniquePrices)
        .sort((a, b) => b - a) // Numeric descending sort
        .forEach((price) => {
          const option = document.createElement("option");
          option.value = price;
          option.textContent = `$${price}`;
          priceFilter.appendChild(option);
        });

        priceFilter.addEventListener("change", (event) => {
          const selectedPrice = event.target.value;
          filterPlacesByPrice(selectedPrice);
        });
    }
  } catch (error) {
    console.error("Error fetching places:", error);
  }
}

function getPlaceIdFromURL() {
  // Extract the place ID from window.location.search
  // Your code here
  const params = new URLSearchParams(window.location.search);
  return params.get('place_id');
}


async function fetchPlaceDetails(token, place_id) {
  // Make a GET request to fetch place details
    // Include the token in the Authorization header
  try {
    const response = await fetch(`http://127.0.0.1:5000/api/v1/places/${place_id}`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    });
    
    // Handle the response and pass the data to displayPlaceDetails function
    if (response.ok) {
      const place = await response.json();

      displayPlaceDetails(place);

    } else {
      console.error('Failed to fetch place details:', response.statusText);
    }
  
  } catch (error) {
  console.error('Error fetching place details:', error);
}
}


function displayPlaceDetails(place) {
  const placeDetailsSection = document.getElementById('place-details');
  // Clear the current content of the place details section
  placeDetailsSection.innerHTML = "";
  // Create elements to display the place details (name, description, price, amenities and reviews)
  placeDetailsSection.innerHTML = `
        <h2>${place.title}</h2>
        <p><strong>Host:</strong> ${place.owner.first_name} ${place.owner.last_name}</p>
        <p><strong>Price per night:</strong> $${place.price}</p>
        <p><strong>Description:</strong> ${place.description}</p>
        <p><strong>Amenities:</strong> ${place.amenities && Array.isArray(place.amenities) && place.amenities.length > 0 
          ? place.amenities.map(amenity => amenity.name).join(', ')
          : 'No amenities listed'}
        </p>

    `;
  const placeElement = document.createElement('div');
  // Append the created elements to the place details section
  placeDetailsSection.appendChild(placeElement);
}