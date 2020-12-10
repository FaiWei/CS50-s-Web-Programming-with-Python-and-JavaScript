let user_route; //global used to slightly filter content for anonimous user (likes, profiles)

document.addEventListener('DOMContentLoaded', function() {
    try {
        user_route = `${document.querySelector('#profile-name').dataset.id}`; // создание исключения
        document.querySelector('#profile').addEventListener('click', () => LoadProfile(user_route));
        document.querySelector('#following').addEventListener('click', () => LoadFeed('following', user_route, 1));
     }
     catch (e) {
        if (e instanceof TypeError) {
            user_route = 0;
        }
     }

    document.querySelector('#posts').addEventListener('click', () => LoadFeed('posts', user_route, 1));

    // Send message
    if (user_route > 0) {
        document.querySelector('#send-message').onclick = function() {
            fetch('/send_message', {
            method: 'POST',
            body: JSON.stringify({
                body: document.querySelector('#message-body').value
            })
            })
            .then(response => response.json())
            .then(result => {
                console.log(result);
                setTimeout(function () {
                    LoadFeed('posts', '0', 1);
                }, 0100);
                
            });
            return false;
        }
    }

    LoadFeed('posts', '0', 1);
});


function LoadProfile(user_id) { 
    document.querySelector('#net-feed-name').innerHTML = 'Profile';
    document.querySelector('#net-feed').style.display = 'block';
    if (user_route == 0) {
        LoadMessage(NotForAnonim());
    } else {
        LoadFeed('profile', user_id, 1)
        fetch(`load_profile/${user_id}`)
        .then(response => response.json())
        .then(user_info => {
            CreateProfile(user_info);
        })
    }
}


function CreateProfile(user_info) {

    document.querySelector('#net-profile').innerHTML = '';

    const element = document.createElement('div');
    element.className = `profile-element card custom-margine`;
    const nickname_box = document.createElement('h5');
    nickname_box.className = `card-header`;
    nickname_box.style.backgroundColor = "rgb(113, 222, 215)";
    nickname_box.innerHTML = `<div class="row"><div class="col-sm"><b>${user_info.username}</b></div></div>`; 
    element.append(nickname_box);
    const message_box = document.createElement('div');
    message_box.className = `card-body`;
    message_box.style.backgroundColor = "rgb(237, 253, 252)";
    message_box.innerHTML = `<p class="card-text"><div style="font-size:18px"><b>Followers</b>: <span id = "p${user_info.id}">${user_info.followers}</span></div><br><div style="font-size:18px"><b>Favorited</b>: ${user_info.favorite}</div></p>`;
    element.append(message_box);
    fetch(`check_favorite/${user_info.id}`)
    .then(response => response.json())
    .then(check_info => { 
        if (check_info.info == false) {
            element.append(FavoriteButton(check_info.status, user_info.id));
        }
    })
    document.querySelector('#net-profile').append(element);
}


function FavoriteButton(check_info, user_id) {
    let id = parseInt(user_id)
    let buttonName = 'Favorite';
    let favoriteStatus = true;
    if (check_info) {
    buttonName = 'Unfavorite';
    favoriteStatus = false; 
        }
    const button = document.createElement('button');
    button.className = `btn btn-sm btn-outline-primary archive`;  
    button.innerHTML = `${buttonName}`;
    button.addEventListener('click', function() {
        fetch(`/load_profile/${id}`, {
            method: 'PUT',
            body: JSON.stringify({
                status: favoriteStatus
                }),
            })
        let count = parseInt(document.querySelector(`#p${user_id}`).innerHTML);    
        button.replaceWith(FavoriteButton(favoriteStatus, user_id));
        if (favoriteStatus) {
            document.querySelector(`#p${user_id}`).innerHTML = count + 1;
        } else {
            document.querySelector(`#p${user_id}`).innerHTML = count - 1;
        }
    });
    return button;
}


function LoadFeed(type, user_id, page) {

    // Show compose view and hide other views
    document.querySelector('#net-feed-area').innerHTML = '';
    document.querySelector('#net-profile').style.display = 'none';
    if (type == 'following') {
        document.querySelector('#net-feed-name').innerHTML = 'Following';
        document.querySelector('#net-newpost').style.display = 'none';
    } else if (type == 'profile') {
        document.querySelector('#net-newpost').style.display = 'none';
        document.querySelector('#net-profile').style.display = 'block';        
    }
    else {
        if (type == 'posts') {
            document.querySelector('#net-feed-name').innerHTML = 'All Posts';
        }
        if (user_route > 0) {
            document.querySelector('#message-body').value = '';
            document.querySelector('#net-newpost').style.display = 'block';
        }
    }
    document.querySelector('#net-feed').style.display = 'block';
    // Fetch messages
    fetch(`/messages/${type}/${user_id}/${page}`)
    .then(response => response.json())
    .then(messages => {
    messages["Messages"].forEach((message) => {
        LoadMessage(message);
    })
    page_max = messages["Num"];
    if (page_max > 1) {
        document.querySelector('#net-feed-area').prepend(PagiBar(type, user_id, page, page_max));
        document.querySelector('#net-feed-area').append(PagiBar(type, user_id, page, page_max));
    }
  });

}


function LoadMessage(message) {
    const element = document.createElement('div');
    element.className = `card custom-margine`;
    const nickname_box = document.createElement('h5');
    nickname_box.className = `card-header`;
    nickname_box.innerHTML = `<div class="row"><div class="col-sm"><b>${message.username}</b></div><div class="col-sm align="right"><b>Time</b>: ${message.timestamp}</div></div>`;
    if (message.id > 0) {  
        nickname_box.addEventListener('click', function() {
            LoadProfile(message.user_id);
        }); 
    }
    element.append(nickname_box);

    const message_box = document.createElement('div');
    message_box.className = `card-body`;
    message_box.id = `b${message.id}`;
    element.append(message_box);
    message_box.append(MessageBody(message));
    document.querySelector('#net-feed-area').append(element);
}



function MessageBody(message) {
    const div_row = document.createElement('div');
    div_row.className = `row`;    

    const col_body = document.createElement('div');
    col_body.className = `col-sm-11`; 
    col_body.innerHTML = `<p class="card-text"><div style="font-size:18px">${message.body}</div></p>`;
    div_row.append(col_body);    
    const col_button = document.createElement('div');
    col_button.className = `col-sm-1`;
    div_row.append(col_button); 

    if (message.id > 0) { 
        col_button.append(Heart(message.liked, message.id, message.likes));   
    }

    if (message.user_id == user_route && user_route != 0) { 
        col_button.append(EditButton(message));
    };

    return div_row;
}


function Heart(message_liked, message_id, message_likes) {
    let heartImg = 'heart-grey.png';
    let likeStatus = true;
    let countStatus = message_likes + 1;
    if (message_liked) {
        heartImg = 'heart-liked.png';
        likeStatus = false;
        countStatus = message_likes - 1;
        }
    if (message_likes == 0)
    heartImg = 'heart-blank.png';
    const like_table = document.createElement('table');
    const like_tr1 = document.createElement('tr');
    like_table.append(like_tr1);
    const like_td1 = document.createElement('td');
    like_tr1.append(like_td1);        
    const like = document.createElement('img');
    like.alt = 'Like';
    like.style.margin = "0 auto";
    like.src = `${DJANGO_STATIC_URL}/static/network/${heartImg}`;
    like_td1.append(like);
    const like_tr2 = document.createElement('tr');
    like_table.append(like_tr2);
    const like_td2 = document.createElement('td');
    like_tr2.append(like_td2);  
    const like_count = document.createElement('p');
    like_count.innerHTML = message_likes;
    like_count.style.textAlign = 'center';
    like_count.style.fontWeight = 'bold';
    like_count.style.fontSize = '18px';
    like_td2.append(like_count);
    if (user_route > 0) {
        like.addEventListener('click', function() {
            fetch(`/message/${message_id}`, {
                method: 'PUT',
                body: JSON.stringify({
                    liked: likeStatus
                    }),
                })
            like_table.replaceWith(Heart(likeStatus, message_id, countStatus));
        });
    }
    return like_table;
}


function EditButton(message) { 
    const button = document.createElement('button');
    button.className = `btn btn-sm btn-outline-primary`;  
    button.innerHTML = `Edit`;
    button.addEventListener('click', function() {
        document.querySelector(`#b${message.id}`).innerHTML = '';
        document.querySelector(`#b${message.id}`).append(EditMessage(message));
    });
    return button;
}


function EditMessage(message) {
    const form_element = document.createElement('form');
    form_element.className = `input-group`;

    const textarea_box = document.createElement('textarea');
    textarea_box.className = `form-control`;
    textarea_box.id = `e${message.id}`;    
    textarea_box.setAttribute('aria-label', 'With textarea');
    textarea_box.innerHTML = `${message.body}`; 
    form_element.append(textarea_box);

    const append_button_box = document.createElement('div');
    append_button_box.className = `input-group-append`;
    form_element.append(append_button_box);

    const edit_button = document.createElement('button');
    edit_button.className = `btn btn-primary`;
    edit_button.innerHTML = `Edit`;
    append_button_box.append(edit_button);
    edit_button.addEventListener('click', function() {
        message.body = document.querySelector(`#e${message.id}`).value
        fetch(`/message/${message.id}`, {
            method: 'PUT',
            body: JSON.stringify({
                edit_body: message.body
                }),
            })
        document.querySelector(`#b${message.id}`).innerHTML = '';
        document.querySelector(`#b${message.id}`).append(MessageBody(message));
        return false;
    });
    return form_element;
}


function PagiBar(type, user_id, page, page_max) {
    let refList = [];
    let prevDisable = '';
    let nextDisable = '';
    let li_3Disable = '';
    let li_1Active = '';
    let li_2Active = " active";
    let page_input = page;
    if (page == 1) {
        prevDisable = " disabled";
        li_1Active = " active";
        li_2Active = '';
        page_input = page_input + 1;
    }
    if (page_max == 2) {
        li_3Disable = " disabled";
    }
    if (page_max == page) {
        li_3Disable = " disabled";        
        nextDisable = " disabled";

    }
    const nav = document.createElement('nav');
    nav.setAttribute('aria-label', 'Pagination');

    const ul = document.createElement('ul');
    ul.className = `pagination`;
    nav.append(ul);

    const prev = document.createElement('li'); 
    prev.className = `page-item${prevDisable}`;
    ul.append(prev);
    const prev_span = document.createElement('span');
    prev_span.className = `page-link`;
    prev_span.innerHTML = 'Previous';
    prev_span.value = (page_input - 1);
    prev.append(prev_span);
    if (prevDisable == '') {refList.push(prev);}

    const li_1 = document.createElement('li'); 
    li_1.className = `page-item${li_1Active}`;
    ul.append(li_1);
    const li_1_span = document.createElement('span');
    li_1_span.className = `page-link`;
    li_1_span.innerHTML = (page_input - 1);
    li_1_span.value = (page_input - 1);
    li_1.append(li_1_span); 
    refList.push(li_1);

    const li_2 = document.createElement('li'); 
    li_2.className = `page-item${li_2Active}`;
    ul.append(li_2);
    const li_2_span = document.createElement('span');
    li_2_span.className = `page-link`;
    li_2_span.innerHTML = page_input;
    li_2_span.value = page_input;
    li_2.append(li_2_span);
    refList.push(li_2); 

    const li_3 = document.createElement('li'); 
    li_3.className = `page-item${li_3Disable}`;
    ul.append(li_3);
    const li_3_span = document.createElement('span');
    li_3_span.className = `page-link`;
    li_3_span.innerHTML = (page_input + 1);
    li_3_span.value = (page_input + 1);
    li_3.append(li_3_span); 
    if (li_3Disable == '') {refList.push(li_3);}

    const next = document.createElement('li'); 
    next.className = `page-item${nextDisable}`;
    ul.append(next);
    const next_span = document.createElement('span');
    next_span.className = `page-link`;
    next_span.innerHTML = 'Next';
    next_span.value = (page_input + 1);
    next.append(next_span); 
    if (nextDisable == '') {refList.push(next);}

    refList.forEach((ref) => {
        ref.addEventListener('click', function() {
            LoadFeed(type, user_id, ref.firstChild.value);
        });
    });
    return nav;
}

function NotForAnonim() {
    document.querySelector('#net-feed-area').innerHTML = '';
    let message = {
        username: 'Error',
        timestamp: "---",
        body: "Anonymous user cannot view profile",
        id: 0,
        user_id: 0
    };
    return message;
}