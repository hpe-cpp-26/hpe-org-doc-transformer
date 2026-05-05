const amqp = require("amqplib");   
let channel;


async function connectQueue() {
    const connection = await amqp.connect("amqp://localhost"); 
    channel = await connection.createChannel();

    await channel.assertQueue("event_queue", {
        durable: true
    });

    console.log("RabbitMQ connected");
}


async function pushToQueue(data) {
    if (!channel) {
        console.log("Channel not ready");
        return;
    }

   const result = channel.sendToQueue(
        "event_queue",
        Buffer.from(JSON.stringify(data)),
        { persistent: true }
    );

    console.log("Send result:" , result);
    console.log("Message pushed");
}

module.exports = {
    connectQueue,
    pushToQueue
};