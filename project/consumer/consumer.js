const amqp = require("amqplib");
const dispatch = require("./dispatcher");

async function start() {
  const connection = await amqp.connect("amqp://localhost");
  const channel = await connection.createChannel();

  await channel.assertQueue("event_queue", { durable: true });
  await channel.assertQueue("normalization_queue", { durable: true });

  console.log("Consumer running...");

  channel.consume("event_queue", async (msg) => {
    if (!msg) return;

    const data = JSON.parse(msg.content.toString());

    await dispatch(data, channel);

    channel.ack(msg);
  });
}

start();