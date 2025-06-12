function startTimer(seconds) {
    let timer = seconds;
    const display = document.getElementById('timer');
    const form = document.getElementById('quiz-form');
    const interval = setInterval(function () {
        display.textContent = timer;
        if (timer <= 0) {
            clearInterval(interval);
            alert("Time's up! Submitting the quiz.");
            form.submit();
        }
        timer--;
    }, 1000);
}
