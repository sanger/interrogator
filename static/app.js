// Get the URL parameters
const urlParams = new URLSearchParams(window.location.search);

// Get the form element
const form = document.querySelector("form");

// Set the form values based on the URL parameters

// Set the form values based on the URL parameters
Array.from(form.elements).forEach((element) => {
  const paramName = element.name;
  const paramValue = urlParams.get(paramName);
  if (paramValue) {
    element.value = paramValue;
  }
});
