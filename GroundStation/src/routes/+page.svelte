<script lang="ts">
    import {
        Container,
        Row,
        Col,
        Spinner,
        useColorMode,
    } from "@sveltestrap/sveltestrap";
    import {
        Plot,
        Line,
        Dot,
        Pointer,
        Text,
        Frame,
        GridX,
        GridY,
        AxisX,
        AxisY,
    } from "svelteplot";
    import * as Plotly from "plotly.js-dist-min";
    //import Map from "$lib/Map.svelte";

    const BACKEND_URL = "http://127.0.0.1:8080";
    useColorMode("light");

    let graphs = ["temp", "press", "humidity", "entropy", "height", "altitude"];

    let graphsTitles: Map<string, string> = new Map();
    graphsTitles.set("temp", "Temperature (ºC)");
    graphsTitles.set("press", "Pressure (hPa)");
    graphsTitles.set("humidity", "Relative Humidity (%)");
    graphsTitles.set("entropy", "Entropy (kJ/kg ⋅ K)");
    graphsTitles.set("height", "Height (m)");
    graphsTitles.set("altitude", "Altitude (m)");

    type RowCSV = {
        packetKind: number;
        time: number;
        temp: number;
        press: number;
        humidity: number;
        stabilityClassifier: number;
        linAccX: number;
        linAccY: number;
        linAccZ: number;
        qR: number;
        qY: number;
        qJ: number;
        qK: number;
        rssi: number;
    };

    type RowProcessed = {
        packetKind: number;
        time: number;
        temp: number;
        press: number;
        humidity: number;
        entropy: number;
        altitude: number;
        height: number;
        stabilityClassifier: number;
        x: number;
        y: number;
        z: number;
        rssi: number;
    };

    var dataGlobal: Array<RowProcessed> = $state([]);

    const R = 8.314;
    const G = 9.807;
    const exponente = (0.0065 * R) / (G * 0.0289644);
    const SEALEVEL = 1017.2;

    function calcAltitude(press: number): number {
        return 44330 * (1.0 - Math.pow(press / SEALEVEL, exponente));
    }

    function calcHeight(press: number, P0: number): number {
        return 44330 * (1.0 - Math.pow(press / P0, exponente));
    }

    const ra = 0.28705;
    const rv = 0.4615;
    const cpa = 1.006;
    const cpv = 1.86;

    function calcPressSat(temp: number): number {
        return 0.61078 * Math.exp((17.27 * temp) / (temp + 237.3));
    }

    function calcEntropy(
        temp: number,
        press: number,
        humidity: number,
    ): number {
        temp = Number(temp);
        press = Number(press) / 100;
        humidity = Number(humidity) / 100;
        let psat = calcPressSat(temp);
        let pv = humidity * psat;
        let pa = press - pv;
        let w = 0.622 * (pv / (press - pv));
        let tk = temp + 273.15;
        let sfg0 = 9.156;

        let s =
            cpa * Math.log(tk / 273.15) -
            ra * Math.log(pa / 101.325) +
            w *
                (sfg0 +
                    cpv * Math.log(tk / 273.15) -
                    rv * Math.log(pv / 0.611));
        //console.log("temp: " + temp, "press: " + press, "humidity: " + humidity, "psat: " + psat, "pv: " + pv, "pa: " + pa, "w: " + w, "tk: " + tk, "sfg0: " + sfg0, "s: " + s);
        return s;
    }

    type Vec3 = [number, number, number];
    type Quat = [number, number, number, number];

    // From the RAW Quaternion math Library
    // https://github.com/rawify/Quaternion.js/blob/main/src/quaternion.js#L985-L1020
    /**
     * MIT License
     *
     * Copyright (c) 2025 Robert Eisele
     *
     * Permission is hereby granted, free of charge, to any person obtaining a copy
     * of this software and associated documentation files (the "Software"), to deal
     * in the Software without restriction, including without limitation the rights
     * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
     * copies of the Software, and to permit persons to whom the Software is
     * furnished to do so, subject to the following conditions:
     *
     * The above copyright notice and this permission notice shall be included in all
     * copies or substantial portions of the Software.
     *
     * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
     * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
     * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
     * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
     * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
     * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
     * SOFTWARE.
     */
    function rotateVectorbyQuat(v: Vec3, q: Quat): Vec3 {
        const qw = q[0];
        const qx = q[1];
        const qy = q[2];
        const qz = q[3];

        // Hot path for @rawify/Vector3 like vectors
        const vx = v[0];
        const vy = v[1];
        const vz = v[2];

        // t = q x v
        let tx = qy * vz - qz * vy;
        let ty = qz * vx - qx * vz;
        let tz = qx * vy - qy * vx;

        // t = 2t
        tx = tx + tx;
        ty = ty + ty;
        tz = tz + tz;

        // v + w t + q x t
        const rx = vx + qw * tx + qy * tz - qz * ty;
        const ry = vy + qw * ty + qz * tx - qx * tz;
        const rz = vz + qw * tz + qx * ty - qy * tx;

        return [rx, ry, rz];
    }

    function addVec(vec1: Vec3, vec2: Vec3): Vec3 {
        return [vec1[0] + vec2[0], vec1[1] + vec2[1], vec1[2] + vec2[2]];
    }

    function reshapeCSVLine(
        data: Array<RowCSV>,
        v: RowCSV,
        P0: number,
        currVel: Vec3,
        currPos: Vec3,
        initialAlt: number,
    ) {
        v.packetKind = Number(v.packetKind);
        v.time = Number(v.time);
        v.temp = Number(v.temp);
        v.press = Number(v.press);
        v.humidity = Number(v.humidity);
        v.stabilityClassifier = Number(v.stabilityClassifier);
        v.linAccX = Number(v.linAccX);
        v.linAccY = Number(v.linAccY);
        v.linAccZ = Number(v.linAccZ);
        v.qR = Number(v.qR);
        v.qY = Number(v.qY);
        v.qJ = Number(v.qJ);
        v.qK = Number(v.qK);
        v.rssi = Number(v.rssi);
        if (Number(v.packetKind) === 1) {
            let dt =
                data.indexOf(v) == 0
                    ? 0
                    : (v.time - data[data.indexOf(v) - 1].time) / 1000;
            const n = Math.sqrt(
                v.qR * v.qR + v.qY * v.qY + v.qJ * v.qJ + v.qK * v.qK,
            );
            let quat: Quat = [v.qR / n, v.qY / n, v.qJ / n, v.qK / n];

            let accelBody: Vec3 = [v.linAccX, v.linAccY, v.linAccZ];
            let accelWorld = rotateVectorbyQuat(accelBody, quat);

            currVel[0] = currVel[0] + accelWorld[0] * dt;
            currVel[1] = currVel[1] + accelWorld[1] * dt;
            currVel[2] = currVel[2] + accelWorld[2] * dt;

            currPos[0] = currPos[0] + currVel[0] * dt;
            currPos[1] = currPos[1] + currVel[1] * dt;
            currPos[2] = currPos[2] + currVel[2] * dt;
        }

        v.press = v.press / 100;
        console.log(currPos);
        return {
            packetKind: v.packetKind,
            time: v.time / 1000,
            temp: v.temp,
            press: v.press,
            humidity: v.humidity,
            entropy: calcEntropy(v.temp, v.press * 10, v.humidity),
            altitude: calcAltitude(v.press),
            height: calcHeight(v.press, P0),
            stabilityClassifier: v.stabilityClassifier,
            x: currPos ? currPos[0] : 0,
            y: currPos ? currPos[1] : 0,
            z: currPos ? calcAltitude(v.press) - initialAlt : 0,
            rssi: v.rssi,
        };
    }

    function unpack(rows: any, key: any) {
        return rows.map(function (row: any) {
            return row[key];
        });
    }

    function make3DScatter() {
        let points: Array<{ x: number; y: number; z: number }> = [];
        let index = 0;

        for (let item in dataGlobal) {
            if (dataGlobal[item].packetKind == 1) {
                points.push({
                    x: dataGlobal[item].x,
                    y: dataGlobal[item].y,
                    z: dataGlobal[item].z,
                });
            }
        }

        let trace: Partial<Plotly.ScatterData> = {
            x: unpack(points, "x"),
            y: unpack(points, "y"),
            z: unpack(points, "z"),
            mode: "lines+markers",
            marker: {
                size: 4,
                line: {
                    color: "rgba(217, 217, 217, 0.14)",
                    width: 0.5,
                },
                opacity: 0.8,
            },
            type: "scatter3d",
        };
        var layout: Partial<Plotly.Layout> = {
            margin: { l: 30, r: 30, b: 30, t: 30 },
            showlegend: true,
            scene: {
                xaxis: { showaxeslabels: true, title: { text: "x (m)" } },
                yaxis: { showaxeslabels: true, title: { text: "y (m)" } },
                zaxis: { showaxeslabels: true, title: { text: "z (m)" } },
            },
        };

        Plotly.newPlot("manual-graphs", [trace], layout);
    }

    function getSlope(): number {
        return (
            (dataGlobal[200].altitude - dataGlobal[59].altitude) /
            (dataGlobal[200].time - dataGlobal[59].time)
        );
    }

    async function fetchData() {
        const json = await fetch(BACKEND_URL + "/db");
        let jsonContent = await json.text();
        if (json.ok) {
            let data = JSON.parse(jsonContent);

            const P0 = data[0].press / 100;
            let initialAlt = calcAltitude(data[0].press / 100);
            let currVel: Vec3 = [0, 0, 0];
            let currPos: Vec3 = [0, 0, 0];

            for (const key in data) {
                if (Object.prototype.hasOwnProperty.call(data, key)) {
                    const element = data[Number(key)];
                    dataGlobal.push(
                        reshapeCSVLine(
                            data,
                            element,
                            P0,
                            currVel,
                            currPos,
                            initialAlt,
                        ),
                    );
                }
            }

            // TODO: Had to add some additional niceties for the presentation,
            // not sure if this still works properly
            var source = new EventSource(BACKEND_URL + "/subscribe");
            source.addEventListener("data", function (ev: MessageEvent) {
                let json = JSON.parse(ev.data);
                let ret = reshapeCSVLine(
                    data,
                    json as RowCSV,
                    P0,
                    currVel,
                    currPos,
                    initialAlt,
                );
                dataGlobal.push(ret);
                dataGlobal.sort((a, b) => a.time - b.time);
            });

            let Entropys = [];
            for (var i in dataGlobal) {
                Entropys.push(dataGlobal[i].entropy);
            }
            console.log(Math.min(...Entropys), Math.max(...Entropys));
            make3DScatter();
            /*
            let maxAlt = Math.max(...unpack(dataGlobal, "altitude"));
            console.log(maxAlt);
            for (let i in dataGlobal) {
                if (
                    ((dataGlobal as any)[i] as RowProcessed).altitude.toFixed(
                        2,
                    ) == "943.69"
                )
                    console.log("START: " + i);

                if (
                    ((dataGlobal as any)[i] as RowProcessed).altitude.toFixed(
                        2,
                    ) == "145.11"
                )
                    console.log("END: " + i);

                if (
                    ((dataGlobal as any)[i] as RowProcessed).altitude.toFixed(
                        2,
                    ) == (1108.9020264025544).toFixed(2)
                )
                    console.log("MAX: " + i);
                if (
                    ((dataGlobal as any)[i] as RowProcessed).height.toFixed(
                        2,
                    ) == "19.69"
                )
                    console.log("MIN: " + i);
            }
            console.log(
                (
                    ((dataGlobal[206].temp - dataGlobal[26].temp) /
                        (dataGlobal[206].height - dataGlobal[26].height)) *
                    100
                ).toFixed(2) + " m",
            );*/
            return dataGlobal;
        } else {
            throw new Error(jsonContent);
        }
    }
</script>

<Container fluid class="justify-content-center" color="dark-subtle">
    {#await fetchData()}
        <Container fluid color="dark-subtle">
            <Row class="justify-content-center">
                <Col xs="auto">
                    <Spinner type="border" color="primary" />
                </Col>
            </Row>
        </Container>
    {:then data}
        <Container fluid color="dark-subtle">
            <Row class="justify-content-center">
                {#each graphs as name, index}
                    <Col xs="auto">
                        <Plot
                            title={graphsTitles.get(name) + " vs Time (s)"}
                            x={{
                                label: "Time (s)",
                                tickFormat: (d: any) => `${d}`,
                            }}
                            y={{
                                label: graphsTitles.get(name),
                                tickFormat: (d: any) => `${d}`,
                            }}
                            height={400}
                        >
                            <Frame />
                            <GridX />
                            <GridY />
                            <AxisX
                                title="Time (s)"
                                tickFormat={(d: any) => `${d}`}
                            />
                            <AxisY
                                tickFormat={(d: any) => `${d}`}
                                anchor="left"
                                title={graphsTitles.get(name)}
                            />

                            {#if name == "altitude"}
                                <Text
                                    fill="currentColor"
                                    stroke="var(--svelteplot-bg)"
                                    strokeWidth={3}
                                    frameAnchor="right"
                                    text={"Terminal Velocity = " +
                                        getSlope().toFixed(2) +
                                        " m/s"}
                                    dx={-18}
                                />
                            {/if}

                            {#if name == "temp"}
                                <Text
                                    fill="currentColor"
                                    stroke="var(--svelteplot-bg)"
                                    strokeWidth={3}
                                    frameAnchor="right"
                                    text={"Thermal Gradient = " +
                                        (
                                            ((dataGlobal[206].temp -
                                                dataGlobal[26].temp) /
                                                (dataGlobal[206].height -
                                                    dataGlobal[26].height)) *
                                            100
                                        ).toFixed(2) +
                                        " m"}
                                    dx={-18}
                                />
                            {/if}

                            <Line data={dataGlobal} x="time" y={name} />
                            {#if name == "altitude"}
                                <Text
                                    data={[dataGlobal[26]]}
                                    fill="currentColor"
                                    stroke="var(--svelteplot-bg)"
                                    strokeWidth={3}
                                    x="time"
                                    y={name}
                                    text={(d) =>
                                        "(" +
                                        d.time.toFixed(2) +
                                        ", " +
                                        d.altitude.toFixed(2) +
                                        ")"}
                                    lineAnchor="bottom"
                                    fontWeight="bold"
                                    dy={-5}
                                />
                                <Dot
                                    data={[dataGlobal[26]]}
                                    x="time"
                                    y={name}
                                    fill
                                />
                            {/if}
                            <Pointer data={dataGlobal} x="time">
                                {#snippet children({ data })}
                                    <Text
                                        {data}
                                        fill="currentColor"
                                        stroke="var(--svelteplot-bg)"
                                        strokeWidth={3}
                                        x="time"
                                        y={name}
                                        text={(d) =>
                                            (d as any)[name].toFixed(2)}
                                        lineAnchor="bottom"
                                        fontWeight="bold"
                                        dy={-5}
                                    />
                                    <Dot {data} x="time" y={name} fill />
                                {/snippet}
                            </Pointer>
                        </Plot>
                    </Col>
                {/each}
            </Row>
        </Container>
    {/await}
    <Container fluid class="justify-content-center" color="dark-subtle">
        <Row class="justify-content-center">
            <Col xs="auto">
                <div id="manual-graphs"></div>
            </Col>
        </Row>
    </Container>
</Container>

<style>
</style>
