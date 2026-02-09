
document.addEventListener("DOMContentLoaded", function () {
  const container = document.getElementById("devices-container");
  
  const prefix = container.dataset.prefix;       // formset prefix
  const apiUrl = container.dataset.apiUrl;       // API URL
  const addBtn = document.getElementById("add-device");
  const totalForms = document.querySelector(`[name='${prefix}-TOTAL_FORMS']`);
  const emptyFormDiv = document.getElementById("empty-form");
  if (!container || !addBtn || !totalForms || !emptyFormDiv) return;

  // Fetch accessories via API
  async function loadAccessories(deviceId, wrapper, selected = []) {
    const accessoriesContainer = wrapper.querySelector(".checkbox-list");
    accessoriesContainer.innerHTML = "";
    if (!deviceId) return;

    const response = await fetch(`${apiUrl}?device_id=` + deviceId);
    if (!response.ok) return;

    const data = await response.json();
    data.accessories.forEach(acc => {
      const label = document.createElement("label");
      label.classList.add("form-check-label", "d-block");

      const input = document.createElement("input");
      input.type = "checkbox";
      const prefix = wrapper.querySelector("select").name.split('-device')[0];
      input.name = prefix + '-accessories';
      input.value = acc.id;
      input.classList.add("form-check-input", "me-1");
      if (selected.includes(acc.id.toString())) input.checked = true;

      label.appendChild(input);
      label.appendChild(document.createTextNode(acc.name));
      accessoriesContainer.appendChild(label);
    });
  }

  function setupDeviceWrapper(wrapper) {
    const deviceField = wrapper.querySelector("select[id$='-device']");
    if (!deviceField) return;

    const selectedInputs = wrapper.querySelectorAll(".checkbox-list input:checked");
    const selectedValues = Array.from(selectedInputs).map(i => i.value);

    if (deviceField.value) loadAccessories(deviceField.value, wrapper, selectedValues);

    deviceField.addEventListener("change", function () {
      loadAccessories(this.value, wrapper, []);
    });
  }

  container.querySelectorAll(".device-item").forEach(setupDeviceWrapper);

  addBtn.addEventListener("click", function () {
    const formIndex = parseInt(totalForms.value, 10);
    const newFormHtml = emptyFormDiv.innerHTML.replace(/__prefix__/g, formIndex);
    const wrapperCol = document.createElement("div");
    wrapperCol.classList.add("col-md-4", "p-1");
    wrapperCol.innerHTML = newFormHtml;
    container.appendChild(wrapperCol);
    totalForms.value = formIndex + 1;
    setupDeviceWrapper(wrapperCol.querySelector(".device-item"));
  });

  container.addEventListener("click", function (e) {
    if (e.target.closest(".remove-device")) {
      const item = e.target.closest(".device-item");
      const deleteField = item.querySelector("input[type='checkbox'][name$='-DELETE']");
      if (deleteField) {
        deleteField.checked = true;
        item.style.display = "none";
      } else {
        item.remove();
        totalForms.value = parseInt(totalForms.value, 10) - 1;
      }
    }
  });
});
