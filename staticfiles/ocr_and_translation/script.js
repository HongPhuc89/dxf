$(function() {
  var $context = $(".context");
  var $form = $("form");
  var $button = $form.find("button[name='perform']");
  var $input = $form.find("input[name='keyword']");

  $button.on("click.perform", function() {

    // Determine search term
    var searchTerm = $input.val();

    // Determine options
    var options = {};
    var values = $form.serializeArray();
    /* Because serializeArray() ignores unset checkboxes */
    values = values.concat(
      $form.find("input[type='checkbox']:not(:checked)").map(
        function() {
          return {
            "name": this.name,
            "value": "false"
          }
        }).get()
    );
    $.each(values, function(i, opt){
      var key = opt.name;
      var val = opt.value;
      if(key === "keyword" || !val){
        return;
      }
      if(val === "false"){
        val = false;
      } else if(val === "true"){
        val = true;
      }
      options[key] = val;
    });


    console.log(searchTerm);
    console.log(values);
//    var context = document.querySelector(".context");
//    var instance = new Mark(context);
//    instance.mark(searchTerm, values);
//

  });
  $button.trigger("click.perform");
});