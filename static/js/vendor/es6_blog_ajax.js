function check_labels(labels_array) {
    if(labels_array.length < 1) {
        return false;
    }
    for (y = 0; y < labels_array.length; y++) {
        if (labels_array[y]['name'] == "{{ content.label }}") { // content.label is the value assigned to the label var in its section. This filters issues based on variables
            return true;
        }
        if (y == labels_array.length - 1) {
            return false;
        }
    }
}
function loadComments(data) {
    var blog_count = 0;
	for(i = 0; i < data.length; i++) {
        if(check_labels(data[i]['labels']) == false) {
            continue;
        }
        if(blog_count == 0) {
            document.getElementById("joeblogs").innerHTML = "";
            blog_count = blog_count + 1;
        }
        if (blog_count == 5) {
            break; // only show last 5 blogs
        }
		if(data[i]['state'] == "open") { // can't delete issues, so just delete a blog by closing its issue
			$.ajax(data[i]['comments_url'] + "?access_token=3d0c98b0366aef2c11e02164784288a8d7cb7732", { // This token has read only access for this organisation, which is public. So don't go getting any ideas...
				blog_data: data[i],
				headers: {Accept: "application/vnd.github.full+json"},
				success: function(msg){
					showblog(msg, this.blog_data); // only generate html for the blog if both blog and comments are retrieved
				},
				fail: function() {
					document.getElementById("joeblogs").innerHTML = "Can't retrieve comments, please try again later";
				}
			});
		}
	}
}
function showblog(comment_data, blog_data) {
	//console.log(blog_data);
	const blog_var_mappings = {
		blog_title: blog_data['title'],
		blog_text: blog_data['body'],
		blog_author: blog_data['user']['login'],
		blog_author_url: blog_data['user']['html_url'],
		blog_creation: new Date(blog_data['created_at']).toDateString(),
		blog_id: blog_data['id'],
		blog_url: blog_data['html_url'],
		comment_number: comment_data.length
	}
	const blog_markup = `
				<div class="small-12 center">										
					<h1>${blog_var_mappings.blog_title}</h1>
				</div>
				<div class="small-offset-1 small-10">
					<p class="">${blog_var_mappings.blog_text}</p>
				</div>
				<div class="small-offset-2 small-5">
					<a href="${blog_var_mappings.blog_author_url}">Created By ${blog_var_mappings.blog_author}</a>
				</div>
				<div class="small-4">
					<p class="">Posted On ${blog_var_mappings.blog_creation}</p>
				</div>
				<div style="display: none;" id="${blog_var_mappings.blog_id}" class="small-12">
					
				</div>
				<div class="small-offset-1 small-5">
					${blog_var_mappings.comment_number > 0 ? `<a href="javascript:show_hide(${blog_var_mappings.blog_id})">`+ blog_var_mappings.comment_number + " Comment(s), Click To Toggle View" +`</a>` : `<p>No Comments</p>`}
				</div>
				<div class="small-5">
					<a href="${blog_var_mappings.blog_url}">{% if content.comment %}{{ content.comment }}{% else %}Want To Add Your Thoughts? Click Here To Comment{% endif %}</a>
				</div>
	`;
	document.getElementById("joeblogs").innerHTML += blog_markup;
	for(x = 0; x < comment_data.length; x++) {
		var  seconds_since_comment = Math.round((new Date()).getTime() / 1000) - Math.round(new Date(comment_data[x]['created_at']).getTime()/1000);
		if(seconds_since_comment < 60) {
			var time_since = Math.floor(seconds_since_comment) + " Seconds Ago";
		}
		else if(seconds_since_comment > 59 && seconds_since_comment < 3600) {
			var time_since = Math.floor(seconds_since_comment/60) + " Minutes Ago";
		}
		else if(seconds_since_comment > 3599 && seconds_since_comment < 86400) {
			var time_since = Math.floor(seconds_since_comment/(60*60)) + " Hours Ago";
		}
		else {
			var time_since = Math.floor(seconds_since_comment/(60*60*24)) + " Days Ago";
		}
		const comment_var_mappings = {
			commenter: comment_data[x]['user']['login'],
			created: time_since,
			content: comment_data[x]['body'],
			avatar: comment_data[x]['user']['avatar_url'],
			url: comment_data[x]['user']['html_url']
		}
		const comments_markup = `
			<div class="grid-container">
				<div class="grid-x grid-margin-x">
					<div class="small-12">
						<div class="grid-container" style="background-color:gray;">
							<div class="grid-x grid-margin-x">
								<div class="small-1">
									<img style="height: 44px; width: 44px;" src="${comment_var_mappings.avatar}">
								</div>
								<div style="margin: auto; vertical-align: middle;" class="small-11">										
									<a href="${comment_var_mappings.url}" >${comment_var_mappings.commenter} commented ${comment_var_mappings.created}</a>
								</div>
							</div>
						</div>
					</div>
					<div class="small-offset-1 small-11 footspace-2">
						<p class="">${comment_var_mappings.content}</p>
					</div>
				</div>
			</div>
		`;
		document.getElementById(blog_data['id']).innerHTML += comments_markup;
	}
}
$.ajax("https://github.dxc.com/api/v3/repos/DigitalTransformationUnitBolt/DTUBoltSite/issues?access_token=3d0c98b0366aef2c11e02164784288a8d7cb7732", {
	headers: {Accept: "application/vnd.github.full+json"},
	success: function(msg){
		loadComments(msg);
	},
	fail: function() {
		document.getElementById("joeblogs").innerHTML = "Can't retrieve blogs, please try again later";
	}
});