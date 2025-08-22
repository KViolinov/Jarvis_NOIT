import sqlite3

async def deleteCheckedRows(): # TODO to finish this method
    def query_db():
        # Searching for activity in table Relay
        conn = sqlite3.connect("jarvis_db.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Step 1: Get all MAC addresses from Devices where TypeID = 1
        cursor.execute("""
            SELECT DeviceMACID FROM Devices
            WHERE TypeID = 1
        """)
        mac_addresses = [row["DeviceMACID"] for row in cursor.fetchall()]

        if not mac_addresses:
            print("[nqma zapisi]")  # No records found
        else:
            for mac in mac_addresses:
                print(f"Processing MAC: {mac}")

                # Step 2: Find the latest record's TimeOfRecord for this MAC
                cursor.execute("""
                    SELECT TimeOfRecord FROM Relay
                    WHERE DeviceMACID = ?
                    ORDER BY TimeOfRecord DESC
                    LIMIT 1
                """, (mac,))
                latest_record = cursor.fetchone()

                latest_time = latest_record["TimeOfRecord"] if latest_record else None

                # Step 3: Delete all rows for this MAC where Checked=1 except the latest one
                if latest_time:
                    cursor.execute("""
                        DELETE FROM Relay
                        WHERE DeviceMACID = ?
                        AND Checked = 1
                        AND TimeOfRecord != ?
                    """, (mac, latest_time))

                    deleted_count = cursor.rowcount
                    print(f"Deleted {deleted_count} rows for MAC {mac}, kept latest at {latest_time}")
                else:
                    print(f"No records found in Relay for MAC {mac}")

        conn.commit()
        conn.close()

        # Searching for activity in table RGB
        conn = sqlite3.connect("jarvis_db.db")
        conn.row_factory = sqlite3.Row  # This allows access by column name
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM RGB
            WHERE Checked = 0
            ORDER BY TimeOfRecord ASC
        """)
        rows = cursor.fetchall()

        if not rows:
            print("[nqma zapisi]")  # No records found
        else:
            for row in rows:
                device_mac = row["DeviceMACID"]
                last_colour = row["LastColour"]
                last_intensity = row["LastIntensity"]
                time_of_record = row["TimeOfRecord"]
                checked = row["Checked"]
                print(f"MAC: {device_mac}, State: {last_colour}, Type: {last_intensity}, Time: {time_of_record}, Checked: {checked}")

                messageToSend = last_colour + " " + last_intensity
                #sendGetToDevice(macAddress=device_mac, message=messageToSend)

                # Delete the current row
                cursor.execute("""
                    DELETE FROM RGB
                    WHERE DeviceMACID = ? AND TimeOfRecord = ?
                """, (device_mac, time_of_record))

                print(f"Deleted row with MAC: {device_mac} and Time: {time_of_record}")

        conn.commit()


        # Searching for activity in table IR
        conn = sqlite3.connect("jarvis_db.db")
        conn.row_factory = sqlite3.Row  # This allows access by column name
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM IR
            WHERE Checked = 0
            ORDER BY TimeOfRecord ASC
        """)
        rows = cursor.fetchall()

        if not rows:
            print("[nqma zapisi]")  # No records found
        else:
            for row in rows:
                device_mac = row["DeviceMACID"]
                last_code_sent = row["LastCodeSent"]
                time_of_record = row["TimeOfRecord"]
                checked = row["Checked"]
                print(f"MAC: {device_mac}, State: {last_state}, Code: {last_code_sent}, Time: {time_of_record}, Checked: {checked}")

                #sendGetToDevice(macAddress=device_mac, message=last_code_sent)

                # Delete the current row
                cursor.execute("""
                    DELETE FROM IR
                    WHERE DeviceMACID = ? AND TimeOfRecord = ?
                """, (device_mac, time_of_record))

                print(f"Deleted row with MAC: {device_mac} and Time: {time_of_record}")

        conn.commit()


    await asyncio.to_thread(query_db)