//console.log(`user check initiated`);
document.addEventListener('DOMContentLoaded', () => {
    // log in user info
    const request = new XMLHttpRequest();
    request.open('GET', '/usercheck');
    request.onload = () => {
        const response = JSON.parse(request.response);
        if (response.success) {            
            const nickname = response.user;
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
        li.innerHTML = data.ChannelNameEmit;

        // Add new item to task list
        document.querySelector('#channelList').append(li);
        document.querySelector('#brrValue').innerHTML += data.ChannelNameEmit + '.';;
    });
});

