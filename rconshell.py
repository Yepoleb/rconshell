#!/usr/bin/python3
import readline
import argparse
import basicrcon


def connect(host, port, password):
    conn = basicrcon.RconConnection((host, port))
    try:
        conn.authenticate(password)
    except basicrcon.AuthenticationError:
        print("Authentication failed!")
        conn.close()
        exit(1)
    return conn

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("host")
    parser.add_argument("port", type=int)
    parser.add_argument("password")
    args = parser.parse_args()

    conn = connect(args.host, args.port, args.password)

    while True:
        try:
            cmd = input("$ ")
        except EOFError:
            print("Bye")
            break
        except KeyboardInterrupt:
            continue

        if cmd in ("quit", "exit"):
            print("Bye")
            break

        try:
            if cmd != "more":
                conn.execute(cmd)
            print(conn.response(), end='')
        except Exception as e:
            print(e)
            print("Error occured, reconnecting...")
            conn.close()
            conn = connect(args.host, args.port, args.password)

    conn.close()

if __name__ == "__main__":
    main()
