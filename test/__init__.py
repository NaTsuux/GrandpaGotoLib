import core

if __name__ == '__main__':
    # main = core.preserve
    main = core.reserve
    main.set_log_level(0)
    main.set_timer(None)
    # main.set_timer("01:00:00")
    main.pickup()
