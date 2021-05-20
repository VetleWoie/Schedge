async function confirmform() {
	const form = $("#msform")[0];

	// Post data using the Fetch API
	return await fetch(form.action, {
		method: form.method,
		body: new FormData(form),
	}).then((response => {
		if (!response.ok) {
			response.text().then(txt => {
				errors = JSON.parse(txt)
				Object.keys(errors).forEach(field => {
					fielderrors = errors[field]
					fielderrors.forEach(error => {
						target = $(`#id_${field}`)
						target.css('border', "thin solid red")
						if (field === "duration") {
							// duration form must be handled differently
							formelements = document.getElementsByClassName("duration-form")
							for (var i = 0; i < formelements.length; i++) {
								formelements[i].setCustomValidity(error.message)
							}
						} else {
							target.get(0).setCustomValidity(error.message)
						}
						// Click our way back to the first section
						// delay looks cool
						setTimeout(() => {  $("#previous5").click(); }, 0);
						setTimeout(() => {  $("#previous4").click(); }, 300);
						setTimeout(() => {  $("#previous3").click(); }, 600);
						setTimeout(() => {  $("#previous2").click(); }, 900);
					});
				});
			});
			return -1;  // -1 means we should not go to the final section
		} else {
			// 0 means the form was ok
			var go2event_btn = document.getElementById("event_url")
			go2event_btn.href = response.url
		
			return 0;
		}
	}));
}


$(document).ready(() => {

	var current_fs, next_fs, previous_fs; //fieldsets
	var opacity;

	$(".next").click(async function () {
		// we should not go to next if it is the last input and the form has errors
		if ($(this).attr("id") === "next5") {
			var ret = await confirmform()
			if (ret === -1) {
				return false;
			}
		}
		current_fs = $(this).parent();
		next_fs = $(this).parent().next();

		//Add Class Active
		$("#progressbar li").eq($("fieldset").index(next_fs)).addClass("active");

		//show the next fieldset
		next_fs.show();
		//hide the current fieldset with style
		current_fs.animate({ opacity: 0 }, {
			step: function (now) {
				// for making fielset appear animation
				opacity = 1 - now;

				current_fs.css({
					'display': 'none',
					'position': 'relative'
				});
				next_fs.css({ 'opacity': opacity });
			},
			duration: 600
		});
	});

	$(".previous").click(function () {
		console.log("pressed prev")
		current_fs = $(this).parent();
		previous_fs = $(this).parent().prev();

		//Remove class active
		$("#progressbar li").eq($("fieldset").index(current_fs)).removeClass("active");

		//show the previous fieldset
		previous_fs.show();

		//hide the current fieldset with style
		current_fs.animate({ opacity: 0 }, {
			step: function (now) {
				// for making fielset appear animation
				opacity = 1 - now;

				current_fs.css({
					'display': 'none',
					'position': 'relative'
				});
				previous_fs.css({ 'opacity': opacity });
			},
			duration: 600
		});
	});

	$('.radio-group .radio').click(function () {
		$(this).parent().find('.radio').removeClass('selected');
		$(this).addClass('selected');
	});

	$('#msform').on('keyup keypress', function (e) {
		var keyCode = e.keyCode || e.which;
		if (keyCode === 13 && !$(document.activeElement).is('textarea')) {
			e.preventDefault();
			return false;
		}
		return true;
	});

});
