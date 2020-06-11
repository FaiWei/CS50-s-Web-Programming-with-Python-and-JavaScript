//console.log(`user check initiated`);
document.addEventListener('DOMContentLoaded', () => {
    // log in user info
    let nickname;
    const request = new XMLHttpRequest();
    request.open('GET', '/usercheck');
    request.onload = () => {
        const response = JSON.parse(request.response);
        if (response.success) {            
            nickname = response.user;
            let helloUserDiv = document.querySelector('#helloUser');
            helloUserDiv.innerHTML += nickname + '.';
        }
    } 
    request.send();
    // message exchange with public share
    let connectionTie = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
    connectionTie.on('connect', () => {
        document.querySelector('#createChannelButton').onclick = () => {
            const ChannelName = document.querySelector('#inputChannelName').value;
            connectionTie.emit('submit channel name', {'channel_name': ChannelName});
            document.querySelector('#inputChannelName').value = '';
            // Stop form from submitting
            return false;
        };
    })
    // When a new vote is announced, add to the unordered list
    connectionTie.on('share channel name', data => {
        // Create new item for list
        console.log('we are here bro');
        const li = document.createElement('li');
        const channelLink = document.createElement('li');
        channelLink.href = "";
        channelLink.class = "channel-link";
        channelLink.dataset.link = `${data.ChannelNameEmit}`;
        channelLink.innerHTML = `${data.ChannelNameEmit}`;
        li.append(channelLink);

        // Add new item to task list
        document.querySelector('#channelList').append(li);
        let brrValue = document.querySelector('#brrValue');
        brrValue.innerHTML = `Last broadcast value: ${data.ChannelNameEmit}.`;
    });
});

