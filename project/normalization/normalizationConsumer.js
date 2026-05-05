const amqp = require("amqplib");
const { normalize } = require("./normalizer");

const RABBITMQ_URL = process.env.RABBITMQ_URL || "amqp://localhost";
const INPUT_QUEUE = "normalization_queue";
const OUTPUT_QUEUE = "normalized_events";

async function startNormalizationConsumer() {
  const connection = await amqp.connect(RABBITMQ_URL);
  const channel = await connection.createChannel();

  await channel.assertQueue(INPUT_QUEUE, { durable: true });
  await channel.assertQueue(OUTPUT_QUEUE, { durable: true });

  
  channel.prefetch(1);

  console.log(`[Normalizer] Listening on "${INPUT_QUEUE}" → publishing to "${OUTPUT_QUEUE}"`);

  channel.consume(INPUT_QUEUE, async (msg) => {
    if (!msg) return;

    let raw;
    try {
      raw = JSON.parse(msg.content.toString());
      console.log("[Normalizer] Raw message:", JSON.stringify(raw, null, 2));
    } catch (parseErr) {
      console.error("[Normalizer] Failed to parse message:", parseErr.message);
      channel.nack(msg, false, false);
      return;
    }

    try {
      const normalized = normalize(raw);
       console.log("[Normalized Output]:", JSON.stringify(normalized, null, 2));

     

      channel.sendToQueue(
        OUTPUT_QUEUE,
        Buffer.from(JSON.stringify(normalized)),
        { persistent: true }
      );

      console.log(
        `[Normalizer] ✓ ${normalized.source} | ${normalized.type} | id=${normalized.id}`
      );

      channel.ack(msg);
    } catch (normErr) {
      console.error(
        `[Normalizer] ✗ Failed to normalize message from source="${raw?.source}":`,
        normErr.message
      );
     
      channel.nack(msg, false, false);
    }
  });
}

startNormalizationConsumer().catch((err) => {
  console.error("[Normalizer] Fatal startup error:", err);
  process.exit(1);
});