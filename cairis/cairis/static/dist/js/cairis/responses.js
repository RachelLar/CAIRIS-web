/**
 * Created by Raf on 8/06/2015.
 */
$("#responsesTable").click(function () {
    createResponsesTable();
});
$(document).on('click', ".editResponseButton", function () {
    var name = $(this).val();
    $.ajax({
        type: "GET",
        dataType: "json",
        accept: "application/json",
        data: {
            session_id: String($.session.get('sessionID'))
        },
        crossDomain: true,
        url: serverIP + "/api/responses/name/" + name,
        success: function (data) {
            // console.log(JSON.stringify(rawData));
            fillOptionMenu("fastTemplates/editResponseOptions.html", "#optionsContent", null, true, true, function () {

                    switch (data.theResponseType){
                        case "Transfer":
                            toggleResponse("#transferWindow");
                            break;
                        case "Prevent":
                            toggleResponse("#mitigateWindow");
                            break;
                        case "Accept":
                            toggleResponse("#acceptWindow");
                            break;
                    }
                    forceOpenOptions();
                }
            );
        },
        error: function (xhr, textStatus, errorThrown) {
            debugLogger(String(this.url));
            debugLogger("error: " + xhr.responseText + ", textstatus: " + textStatus + ", thrown: " + errorThrown);
        }
    });
});

function toggleResponse(window){
        $("#mitigateWindow").hide();
        $("#acceptWindow").hide();
        $("#transferWindow").hide();
        $(window).show();
}

function createResponsesTable(){
    $.ajax({
        type: "GET",
        dataType: "json",
        accept: "application/json",
        data: {
            session_id: String($.session.get('sessionID'))
        },
        crossDomain: true,
        url: serverIP + "/api/responses",
        success: function (data) {
            window.activeTable = "Respones";
            setTableHeader();
            var theTable = $(".theTable");
            $(".theTable tr").not(function(){if ($(this).has('th').length){return true}}).remove();
            var textToInsert = [];
            var i = 0;

            $.each(data, function(key, item) {
                textToInsert[i++] = "<tr>";
                textToInsert[i++] = '<td><button class="editResponseButton" value="' + key + '">' + 'Edit' + '</button> <button class="deleteResponseButton" value="' + key + '">' + 'Delete' + '</button></td>';

                textToInsert[i++] = '<td name="theName">';
                textToInsert[i++] = key;
                textToInsert[i++] = '</td>';

                textToInsert[i++] = '<td name="theType">';
                textToInsert[i++] = item.theResponseType;
                textToInsert[i++] = '</td>';

                textToInsert[i++] = '</tr>';
            });

            theTable.append(textToInsert.join(''));
            theTable.css("visibility","visible");
            activeElement("reqTable");
            sortTableByRow(0);

        },
        error: function (xhr, textStatus, errorThrown) {
            debugLogger(String(this.url));
            debugLogger("error: " + xhr.responseText +  ", textstatus: " + textStatus + ", thrown: " + errorThrown);
        }
    })
}
