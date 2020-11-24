document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // On submit
  document.querySelector('#compose-form').onsubmit = function() {
    const sendToMail = document.querySelector('#compose-recipients').value;
    fetch('/emails', {
      method: 'POST',
      body: JSON.stringify({
          recipients: document.querySelector('#compose-recipients').value,
          subject: document.querySelector('#compose-subject').value,
          body: document.querySelector('#compose-body').value
      })
    })
    .then(response => response.json())
    .then(result => {
        // Print result
        console.log(result);
    });
    load_mailbox('sent');
    return false; 
  }
  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#mail-view').style.display = 'none';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#mail-view').style.display = 'none';
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  
  // Fetch emails
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    emails.forEach((email) => {
      load_mail(email, mailbox);
    })
  });

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
}

  //Create list of mails
function load_mail(mail, mailbox) {
  let mailColor = 'alert-light';
  if (mail.read == true) {
    mailColor = 'alert-dark';
  }
  console.log(mail)
  const element = document.createElement('div');
  element.className = `alert alert-light`;
  const message = document.createElement('div');
  message.className = `alert ${mailColor}`;
  message.innerHTML = `<div class="row"><div class="col-sm"><b>Sender</b>: ${mail.sender}</div><div class="col-sm" align="right"><b>Time</b>: ${mail.timestamp}</div></div><br><div style="font-size:18px"><b>Theme</b>: ${mail.subject}</div>`;
  message.addEventListener('click', function() {
    load_mail_info(mail.id);
    console.log('Message clicked!');
  });
  element.append(message);
  if (mailbox == 'inbox' || mailbox == 'archive') {
    let buttonName = 'Archive';
    let mailStatusToChange = true;
    if (mailbox == 'archive') {
      buttonName = 'Cancel Archive';
      mailStatusToChange = false;
    }
    const button = document.createElement('button');
    button.className = `btn btn-sm btn-outline-primary archive`;  
    button.innerHTML = `${buttonName}`;
    button.addEventListener('click', function() {
      console.log('Button clicked!');
      fetch(`/emails/${mail.id}`, {
        method: 'PUT',
        body: JSON.stringify({
            archived: mailStatusToChange
        })
      }) 
      load_mailbox(`inbox`);   
    });
    element.append(button);
  }

  const reply = document.createElement('button');
  reply.className = `btn btn-sm btn-outline-primary archive`;  
  reply.innerHTML = `Reply`;
  reply.dataset.id = `${mail.id}`
  reply.addEventListener('click', compose_target_email)
  element.append(reply);
  document.querySelector('#emails-view').append(element);
}

  //Open mail by id: sender, recipients, subject, timestamp, and body
function load_mail_info(mailId) {
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#mail-view').style.display = 'block';
  document.querySelector('#mail-view').innerHTML = `<h3>Mail</h3>`;

  fetch(`/emails/${mailId}`)
  .then(response => response.json())
  .then(email => {
    console.log(email)
    const element = document.createElement('div');
    element.className = `alert alert-dark`;
    element.innerHTML = `<div class="row"><div class="col-sm"><b>Sender</b>: ${email.sender}<br><b>Recipients</b>: ${email.recipients}</div><div class="col-sm" align="right"><b>Time</b>: ${email.timestamp}</div></div><hr><div style="font-size:18px class="row"><b>Theme</b>: ${email.subject}</div><div class="alert alert-light"><b>Body</b><br>${email.body}</div>`;
    const reply = document.createElement('button');
    reply.className = `btn btn-sm btn-outline-primary archive`;  
    reply.innerHTML = `Reply`;
    reply.dataset.id = `${email.id}`
    reply.addEventListener('click', compose_target_email)
    element.append(reply);
    document.querySelector('#mail-view').append(element);
  });

  //readed
  fetch(`/emails/${mailId}`, {
    method: 'PUT',
    body: JSON.stringify({
        read: true
    })
  })     
}

function compose_target_email() {
  compose_email();
  fetch(`/emails/${this.dataset.id}`)
  .then(response => response.json())
  .then(email => {
    console.log(email)
    document.querySelector('#compose-recipients').value = `${email.sender}`;
    if (email.subject.startsWith('Re:')) {
      document.querySelector('#compose-subject').value = `${email.subject}`;
      console.log('2');
    } else {
      console.log('1');
      document.querySelector('#compose-subject').value = `Re: ${email.subject}`;
    }
    document.querySelector('#compose-body').value = `On ${email.timestamp} ${email.recipients} wrote:\n ${email.body}`;
  });
}
