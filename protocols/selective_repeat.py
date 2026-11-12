
"""Selective Repeat ARQ protocol implementation."""

import random


class SelectiveRepeatProtocol:
    """Simulate Selective Repeat ARQ with individual ACKs."""

    MAX_ATTEMPTS = 1000

    def simulate(
        self,
        number_of_frames,
        window_size,
        transmission_delay,
        ack_delay,
        packet_loss,
        ack_loss,
        timeout,
        seed=None
    ):
        # -------------------------------
        # INPUT VALIDATION
        # -------------------------------

        if number_of_frames < 0:
            raise ValueError("Number of frames cannot be negative.")

        if window_size < 1:
            raise ValueError("Window size must be at least 1.")

        if transmission_delay <= 0 or ack_delay < 0:
            raise ValueError("Invalid transmission or ACK delay.")

        if timeout <= 0:
            raise ValueError("Timeout must be positive.")

        if not 0 <= packet_loss <= 100:
            raise ValueError("Packet loss must be between 0 and 100.")

        if not 0 <= ack_loss <= 100:
            raise ValueError("ACK loss must be between 0 and 100.")

        rng = random.Random(seed)

        # -------------------------------
        # PERFORMANCE COUNTERS
        # -------------------------------

        total_transmitted = 0
        retransmissions = 0
        packets_lost = 0
        acks_received = 0
        total_time = 0
        delivered_frames = 0

        # -------------------------------
        # SENDER AND RECEIVER STATE
        # -------------------------------

        base = 0

        acknowledged = [False] * number_of_frames
        receiver_received = [False] * number_of_frames
        attempts = [0] * number_of_frames
        receiver_base = 0

        events = []

        events.append("Selective Repeat simulation started.")

        # -------------------------------
        # MAIN SIMULATION LOOP
        # -------------------------------

        while base < number_of_frames:

            window_end = min(
                base + window_size,
                number_of_frames
            )

            events.append(
                f"\nSender: Window [{base}, {window_end - 1}]"
            )

            # Send only frames that are not acknowledged
            for frame in range(base, window_end):

                if acknowledged[frame]:
                    continue

                attempts[frame] += 1

                if attempts[frame] > self.MAX_ATTEMPTS:
                    raise RuntimeError(
                        f"Frame {frame} exceeded maximum retry limit."
                    )

                total_transmitted += 1

                if attempts[frame] > 1:
                    retransmissions += 1

                events.append(
                    f"Sender: Frame {frame} sent "
                    f"(Attempt {attempts[frame]})"
                )

                total_time += transmission_delay

                # -------------------------------
                # PACKET LOSS
                # -------------------------------

                if rng.random() < packet_loss / 100:

                    packets_lost += 1

                    events.append(
                        f"Network: Frame {frame} LOST"
                    )

                    continue

                # -------------------------------
                # RECEIVER PROCESSING
                # -------------------------------

                ack_frames = []

                if not receiver_received[frame]:

                    receiver_received[frame] = True
                    delivered_frames += 1

                    if frame == receiver_base:

                        events.append(
                            f"Receiver: Frame {frame} received successfully"
                        )

                        while (
                            receiver_base < number_of_frames
                            and receiver_received[receiver_base]
                        ):
                            ack_frames.append(receiver_base)

                            events.append(
                                f"Receiver: Frame {receiver_base} "
                                "delivered to upper layer"
                            )

                            receiver_base += 1

                    else:

                        events.append(
                            f"Receiver: Frame {frame} buffered (out-of-order)"
                        )

                else:

                    events.append(
                        f"Receiver: Duplicate Frame {frame} discarded"
                    )

                    ack_frames.append(frame)

                # -------------------------------
                # INDIVIDUAL ACK GENERATION
                # -------------------------------

                for ack_frame in ack_frames:

                    events.append(
                        f"Receiver: Individual ACK {ack_frame} generated"
                    )

                    total_time += ack_delay

                    # ---------------------------
                    # ACK LOSS
                    # ---------------------------

                    if rng.random() < ack_loss / 100:

                        events.append(
                            f"Network: ACK {ack_frame} LOST"
                        )

                    else:

                        acknowledged[ack_frame] = True
                        acks_received += 1

                        events.append(
                            f"Sender: ACK {ack_frame} received"
                        )

            # -------------------------------
            # SLIDE SENDER WINDOW
            # -------------------------------

            old_base = base

            while (
                base < number_of_frames
                and acknowledged[base]
            ):
                base += 1

            if base > old_base:

                events.append(
                    f"Sender: Window slides from "
                    f"{old_base} to {base}"
                )

            # -------------------------------
            # TIMEOUT AND SELECTIVE RETRANSMISSION
            # -------------------------------

            if base < number_of_frames:

                pending_frames = [
                    frame
                    for frame in range(base, window_end)
                    if not acknowledged[frame]
                ]

                if pending_frames:

                    events.append(
                        "Timeout: Waiting for ACKs of frames "
                        + ", ".join(map(str, pending_frames))
                    )

                    events.append(
                        "Sender: Retransmitting only unacknowledged frames."
                    )

                    total_time += timeout

        events.append(
            "\nSelective Repeat simulation completed."
        )

        # -------------------------------
        # RETURN RESULTS
        # -------------------------------

        return {
            "total_frames_transmitted": total_transmitted,
            "retransmissions": retransmissions,
            "packets_lost": packets_lost,
            "acks_received": acks_received,
            "delivered_frames": delivered_frames,
            "total_time_ms": total_time,
            "events": events
        }
