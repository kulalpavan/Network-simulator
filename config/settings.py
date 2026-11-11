"""Default application settings, scenarios, and protocol descriptions."""

APP_TITLE = "Sliding Window Protocol Simulator"
APP_SUBTITLE = "Visualise how ARQ protocols deliver frames over an unreliable network"
WINDOW_WIDTH = 1320
WINDOW_HEIGHT = 860
MIN_WIDTH = 1280
MIN_HEIGHT = 760

PROTOCOL_ORDER = [
    "One-Bit Sliding Window",
    "Go-Back-N",
    "Selective Repeat",
]

PROTOCOL_INFO = {
    "One-Bit Sliding Window": {
        "short": "Stop-and-Wait",
        "tagline": (
            "Send one frame, then stop and wait for its ACK before "
            "sending anything else."
        ),
        "window_rule": "Window size = 1",
        "ack_rule": "One ACK per frame (0 / 1)",
        "loss_rule": "Timeout → resend same frame",
        "best_for": "Simple links with a low error rate",
        "watch_for": (
            "The sender pauses after every frame until the matching ACK "
            "returns. Lost data or ACKs cause the same frame to be resent."
        ),
        "steps": [
            "Sender transmits frame 0 and starts a timer.",
            "Receiver checks the sequence number and returns ACK 0.",
            "Sender receives the ACK, flips its 0/1 sequence number, and sends frame 1.",
            "A timeout resends the same frame; duplicate copies are detected and discarded.",
        ],
    },
    "Go-Back-N": {
        "short": "Go-Back-N",
        "tagline": (
            "Send a whole window of frames; if one is lost, resend "
            "everything from the missing frame onward."
        ),
        "window_rule": "Window size = N frames",
        "ack_rule": "Cumulative ACKs (ACK n covers up to n)",
        "loss_rule": "Timeout → resend whole window",
        "best_for": "Bursty traffic that needs ordered delivery",
        "watch_for": (
            "After one loss, orange retransmissions restart from the "
            "missing frame, even for frames that already arrived."
        ),
        "steps": [
            "Sender sends every frame inside the window without waiting.",
            "Receiver accepts only the next expected frame and discards out-of-order frames.",
            "Receiver replies with a cumulative ACK for the highest in-order frame.",
            "A timeout rolls the sender back to its base and resends the whole window.",
        ],
    },
    "Selective Repeat": {
        "short": "Selective Repeat",
        "tagline": (
            "Send a window of frames and resend only the specific frames "
            "whose ACKs never arrived."
        ),
        "window_rule": "Window size = N frames",
        "ack_rule": "Individual ACKs for every frame",
        "loss_rule": "Timeout → resend only missing frames",
        "best_for": "Lossy links where bandwidth is precious",
        "watch_for": (
            "Only the missing frames return in orange; frames that already "
            "arrived stay buffered and are never sent twice."
        ),
        "steps": [
            "Sender sends every frame inside the window.",
            "Receiver buffers out-of-order frames and ACKs each frame by number.",
            "Sender marks each acknowledged frame and slides the window forward.",
            "A timeout resends only the frames whose ACKs never arrived.",
        ],
    },
}

SCENARIOS = {
    "Ideal Network": {
        "frames": 20,
        "window": 4,
        "transmission": 10,
        "ack": 5,
        "packet_loss": 0,
        "ack_loss": 0,
        "timeout": 50,
        "seed": 101,
        "description": (
            "A perfect link: no dropped data and no dropped ACKs. "
            "Use it as the baseline."
        ),
    },
    "Packet Loss": {
        "frames": 20,
        "window": 4,
        "transmission": 10,
        "ack": 5,
        "packet_loss": 20,
        "ack_loss": 0,
        "timeout": 50,
        "seed": 202,
        "description": (
            "About 20% of data frames are dropped. Watch how each "
            "protocol recovers."
        ),
    },
    "ACK Loss": {
        "frames": 20,
        "window": 4,
        "transmission": 10,
        "ack": 5,
        "packet_loss": 0,
        "ack_loss": 20,
        "timeout": 50,
        "seed": 303,
        "description": (
            "About 20% of ACKs are lost. Data still arrives, but senders "
            "may time out and resend."
        ),
    },
    "Combined Loss": {
        "frames": 20,
        "window": 4,
        "transmission": 10,
        "ack": 5,
        "packet_loss": 20,
        "ack_loss": 10,
        "timeout": 50,
        "seed": 404,
        "description": (
            "Both data and ACKs are unreliable. This is the hardest "
            "case for every protocol."
        ),
    },
}
