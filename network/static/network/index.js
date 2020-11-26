document.addEventListener('DOMContentLoaded', function() {

    document.querySelector('#profile').addEventListener('click', load_profile);
    document.querySelector('#posts').addEventListener('click', () => load_feed('posts'));
    document.querySelector('#following').addEventListener('click', () => load_feed('following'));


    load_feed('posts');

});

function load_profile() {

    // Show compose view and hide other views
    document.querySelector('#net-profile').style.display = 'block';
    document.querySelector('#net-feed').style.display = 'none';

}

function load_feed(type) {

    // Show compose view and hide other views
    if (type == 'following') {
        document.querySelector('#net-feed-name').innerHTML = 'Following';
    } else {
        document.querySelector('#net-feed-name').innerHTML = 'All Posts';
    }
    document.querySelector('#net-profile').style.display = 'none';
    document.querySelector('#net-feed').style.display = 'block';

}