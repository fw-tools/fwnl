let messageInput = $('.messageinput')
let textArea = $('.textarea')
let screen = $('.screen')

messageInput.on('submit', (e) => {
  e.preventDefault()
  let message = textArea.html().replace(/\n/g, "<br />");

  if (message === '') {
    return
  }

  updateScreen(message, 'user')
  textArea.text('')
  textArea.focus()
  sendChatMessage(message)
})

function updateScreen(message, type) {
  let image = ''
  if (type === 'bot') {
    image = `<div class="image">
      <img src="/img/bot.png" alt="Bot">
    </div>`
  }

  screen.append($(`
    <div class="message ${type}">
      <div class="bubble">
        ${image}
        <div class="time">${formatDate(new Date())}</div>
        <div class="text">${message.trim()}</div>
      </div>
    </div>`))
  screen.scrollTop(screen.prop('scrollHeight'))
}

function sendChatMessage(message) {
  $.ajax({
    type: 'POST',
    url: '/bot',
    data: JSON.stringify({user_data: JSON.parse(window.localStorage.getItem('ud')), text: message}),
    success: (data) => {
      window.localStorage.setItem('ud', JSON.stringify(data.user_data))
      for (var i = 0; i < data.responses.length; i++) {
        updateScreen(data.responses[i], 'bot')
      }
    },
    contentType: "application/json",
    dataType: 'json'
  })
}

function formatDate(date) {
  let hours = date.getHours()
  let minutes = date.getMinutes()

  hours = hours < 10 ? '0' + hours : hours
  minutes = minutes < 10 ? '0' + minutes : minutes

  return hours + ':' + minutes
}

