import logging
from typing import TYPE_CHECKING
from config import get_connection, configure_logging, MQ_EXCHANGE, MQ_ROUTING_KEY
from pika.exceptions import StreamLostError

if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel
    from pika.spec import Basic, BasicProperties

log = logging.getLogger(__name__)


def process_new_message(
    ch: "BlockingChannel", 
    method: "Basic.Deliver",
    properties: "BasicProperties",
    body: bytes
):
    log.warning(f"сообщение получено, обработка... {body}")
    ch.basic_ack(delivery_tag=method.delivery_tag)
    log.warning(f'сообщение {body} обработано')


def consume_message(channel: "BlockingChannel") -> None:
    channel.basic_consume(queue=MQ_ROUTING_KEY, on_message_callback=process_new_message)
    log.warning('ожидание сообщений')
    channel.start_consuming()


def produce_message(channel: "BlockingChannel", message_body: str) -> None:
    queue = channel.queue_declare(queue=MQ_ROUTING_KEY)
    log.info(f'очередь: {queue}')
    log.info(f'отправлено сообщение: {message_body}')
    channel.basic_publish(
        exchange=MQ_EXCHANGE,
        routing_key=MQ_ROUTING_KEY,
        body=message_body
    )
    log.warning(f'опубликовано сообщение: {message_body}')


def main():
    configure_logging(
        # level=logging.DEBUG
    )
    with get_connection() as connection:
        log.info(f'соединение открыто: {connection}')
        with connection.channel() as channel:
            log.info(f'создан канал: {channel}')
            produce_message(channel=channel, message_body='hi')
            consume_message(channel=channel)


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, StreamLostError):
        log.info('соединение закрыто')
        exit(0)