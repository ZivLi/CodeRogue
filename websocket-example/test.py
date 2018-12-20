import webws_client
import asyncio


def main():
    inp = input('----')
    if inp == '1':
        asyncio.get_event_loop().run_until_complete(webws_client.not_goodbye_name())
    else:
        asyncio.get_event_loop().run_until_complete(webws_client.hello())

if __name__ == '__main__':
    main()