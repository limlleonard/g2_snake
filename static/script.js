const size=60; // size of each cell
const radius=25;
let round=1;
let currentScore=0;
let highestScore=0;

function drawSnake(body, food) {
    const board = document.getElementById('board');
    board.innerHTML = '';
    body.forEach(([x,y], index) => {
        const circle = document.createElement('div');
        circle.classList.add('circle');
        if (index===0) {
            circle.classList.add('head');
        }
        circle.style.left = `${x*size+size/2-radius}px`;
        circle.style.top = `${y*size+size/2-radius}px`;
        board.appendChild(circle);
    })
    const circle = document.createElement('div');
    circle.classList.add('circle','food');
    circle.style.left = `${food[0]*size+size/2-radius}px`;
    circle.style.top = `${food[1]*size+size/2-radius}px`;
    board.appendChild(circle);
}
function startStop(button) {
    if (button.innerText === "Start") {
        button.innerText = "Stop";
        startThread();
    } else {
        button.innerText = "Start";
        stopThread();
    }
}
function startThread() {
    const speed=document.getElementById('speed').value;
    const mode=document.getElementById('mode').value;
    const model=document.getElementById('model').value;
    fetch("/start_thread", { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ speed: speed, mode: mode, model: model }) // Send the direction as JSON
    }).catch(err => console.error("Error start thread", err));    
}
function stopThread() {
    fetch("/stop_thread", { 
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
    }).catch(err => console.error("Error stop thread", err));    
}
function pauseResume(button) {
    const action = button.innerText === "Pause" ? "pause" : "resume";
    button.innerText = action === "pause" ? "Resume" : "Pause";
    fetch(`/pause_resume_thread?action=${action}`, { 
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
    }).catch(err => console.error("Error thread", err)); 
}

function resetGame() {
    if (document.getElementById('mode').value==='human') {
        // in human mode, when a round is ended, the player need to press 'start' to restart. Robot start right away
        document.getElementById('btn-start-stop').innerText='Start';
    }
    document.getElementById('btn-pause-resume').innerText='Pause';
    if (highestScore<currentScore) {
        highestScore=currentScore;
        document.getElementById('highestScore').innerText=highestScore;
    }
    round++;
    document.getElementById('round').innerText=round;
    currentScore=0;
    document.getElementById('score').innerText=0;
}
function turn(direction) {
    fetch(`/turn`, { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ direction: direction }) // Send the direction as JSON
    })
    .then(response => response.json())
    .catch(error => console.error('Error:', error));
}
document.addEventListener('DOMContentLoaded', () => {
    // Establish WebSocket connection to Flask-SocketIO
    const socket = io();
    // Listen for 'snake_info' events
    socket.on('snake_info', (data) => {
        // const { body, food, scorePy, plot } = data;
        if (data.scorePy===-1) {
            resetGame();
        } else {
            drawSnake(data.body, data.food);
            if (currentScore<data.scorePy) {
                currentScore=data.scorePy;
                document.getElementById('score').innerText=currentScore;
            }
        }
        if (data.plot) {
            const imgElement = document.getElementById('plot');
            imgElement.src = `data:image/png;base64,${data.plot}`;
        }
    });
});

document.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowLeft') {
        turn('left');
    } else if (event.key === 'ArrowRight') {
        turn('right');
    }
    // else if (event.key === '0') {
    //     startThread();}
});