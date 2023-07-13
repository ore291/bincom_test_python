$(document).ready(function () {
  function isObjEmpty(obj) {
    return JSON.stringify(obj) === "{}";
  }

  $("#addRow").click(function () {
    var tableBody = document.getElementById("results-body");
    var newRow = document.createElement("tr");
    newRow.innerHTML = `<td><input class="form-control" type="text" name="party" ></td><td><input type="number" class="form-control" value="0" name="votes" ></td>`;
    tableBody.appendChild(newRow);
  });

  const get_polling_units = (ward_id) => {
    $.ajax({
      url: "/pu/" + ward_id,
      type: "GET",
      success: function (response) {
        var puSelect = $("#pu_select");
        if (response.length < 1) {
          puSelect.empty();
          puSelect.append("<option value=''>No Polling Unit Found</option>");
        } else {
          puSelect.empty();
          puSelect.append("<option value=''>Select Polling Unit</option>");
          $.each(response, function (index, pu) {
            puSelect.append($("<option></option>").val(pu.id).text(pu.name));
          });
        }
      },
      error: function (error) {
        console.log(error);
      },
    });
  };

  $("#lga_select").change(function () {
    var lgaId = $(this).val();
    $.ajax({
      url: "/wards/" + lgaId,
      type: "GET",
      success: function (response) {
        var wardSelect = $("#ward_select");
        if (response.length < 1) {
          wardSelect.empty();
          wardSelect.append("<option value=''>No Ward Found</option>");
        } else {
          wardSelect.empty();

          $.each(response, function (index, ward) {
            wardSelect.append(
              $("<option></option>").val(ward.id).text(ward.name)
            );
          });

          get_polling_units(response[0].id);
        }
      },
      error: function (error) {
        console.log(error);
      },
    });
  });

  $("#ward_select").change(function () {
    var wardId = $(this).val();
    get_polling_units(wardId);
  });

  $("#results_form").submit(function (e) {
    e.preventDefault();
    var puSelect = $("#pu_select").val();
    if (puSelect != "") {
      $.ajax({
        url: "/get_results/" + puSelect,
        type: "GET",
        success: function (response) {
          var resultsTable = $("#results-table tbody");
          resultsTable.empty();
          if (response.length < 1) {
            alert("Results not found");
          } else {
            sum = 0;
            response.forEach((d) => {
              sum += d.score;
            });
            $.each(response, function (index, result) {
              resultsTable.append(
                "<tr ><td>" +
                  result.name +
                  "</td><td>" +
                  result.score +
                  "</td></tr>"
              );
            });
            resultsTable.append(
              "<tr class='table-active'><td><strong>TOTAL</strong></td><td><strong>" +
                sum +
                "</strong></td></tr>"
            );
          }
        },
        error: function (error) {
          console.log(error);
        },
      });
    } else {
      alert("Select Polling Unit");
    }
  });

  $("#lga_result_select").change(function (e) {
    e.preventDefault();
    var lgaSelect = $("#lga_result_select").val();
    if (lgaSelect != "") {
      $.ajax({
        url: "/lga_results/" + lgaSelect,
        type: "GET",
        success: function (response) {
          var resultsTable = $("#lga-results-table tbody");
          resultsTable.empty();
          if (isObjEmpty(response.results)) {
            alert("Results not found");
          } else {
            $.each(response.results, function (key, value) {
              resultsTable.append(
                "<tr ><td>" + key + "</td><td>" + value + "</td></tr>"
              );
            });
            resultsTable.append(
              "<tr class='table-active'><td><strong>TOTAL</strong></td><td><strong>" +
                response.total +
                "</strong></td></tr>"
            );
          }
        },
        error: function (error) {
          console.log(error);
        },
      });
    } else {
      alert("Select Local Government");
    }
  });
});
