const chat = document.getElementById("chat")
const input = document.getElementById("userInput")
const button = document.getElementById("sendBtn")

button.addEventListener("click", sendMessage)

  input.addEventListener("keypress", function(e){
if(e.key === "Enter"){
   sendMessage()
 }
})

  function getTime(){

const now = new Date()

let hours = now.getHours()
let minutes = now.getMinutes()

const ampm = hours >= 12 ? "PM" : "AM"

hours = hours % 12
hours = hours ? hours : 12

minutes = minutes < 10 ? "0"+minutes : minutes

return hours + ":" + minutes + " " + ampm
}

  function addMessage(text, sender) {

const container = document.createElement("div")
container.classList.add("message", sender)

if(sender === "bot"){

const img = document.createElement("img")
img.src = "Assets/ScrappyFace.png"
img.classList.add("avatar")

const bubble = document.createElement("div")
bubble.classList.add("bubble")
bubble.innerText = text + " (" + getTime() + ")"

container.appendChild(img)
container.appendChild(bubble)

}else{

const bubble = document.createElement("div")
bubble.classList.add("bubble")
bubble.innerText = text + " (" + getTime() + ")"

container.appendChild(bubble)
}

chat.appendChild(container)
chat.scrollTop = chat.scrollHeight
}

  function sendMessage() {

const message = input.value.trim()

 if(message === "") return
  addMessage("You: " + message, "user")

  input.value = ""

 simulateBotResponse(message)
 }


const API_URL = "http://localhost:8000/ask"

async function simulateBotResponse(message) {
  const typing = document.createElement("div")
  typing.classList.add("message", "bot")
  typing.innerText = "ScrappyBOT is typing..."
  chat.appendChild(typing)
  chat.scrollTop = chat.scrollHeight

  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: message })
    })

    if (!res.ok) {
      throw new Error("Server returned " + res.status)
    }

    const data = await res.json()
    typing.remove()

    addMessage("ScrappyBOT: " + data.answer, "bot")

    if (data.sources && data.sources.length > 0) {
      const sourcesText = data.sources
        .map((s, i) => (i + 1) + ". " + s.Title + " — " + s.url)
        .join("\n")
      addMessage("Sources:\n" + sourcesText, "bot")
    }
  } catch (err) {
    typing.remove()
    addMessage(
      "ScrappyBOT: Sorry, I couldn't reach the backend. Make sure the server is running at " + API_URL + ". (" + err.message + ")",
      "bot"
    )
  }
}
