<script lang="ts">
    import {
        Container,
        Row,
        Col,
        Spinner,
    } from "@sveltestrap/sveltestrap";
    import { autoType, dsvFormat } from "d3-dsv";
    import { Plot, Line } from "svelteplot";
    import Map from "$lib/Map.svelte";

    type Row = {
        time: number;
        temp: number;
        press: number;
        columns: Array<String>;
    };
    
    const R = 8.314;
    const G = 9.807;
    const exponente = ( (0.0065 * R) / (G*0.0289644))
    const SEALEVEL = ((1021*100) + (1025*100)) / 2;

    function calcAltitude(press: number, T0: number):number
    {
        return (T0 / 0.0065) * (1.0 - Math.pow ((press*100 / SEALEVEL), exponente))
    }

    function calcAltura(press: number, P0: number, T0: number):number
    {
        return (T0 / 0.0065) * (1.0 - Math.pow ((press*100 / P0), exponente))
    }

    async function fetchData() {
        const csv = await fetch("/theday.csv");
        let csvContent = await csv.text();
        if (csv.ok) {
            csvContent = "time, temp, press\n".concat(csvContent);
            csvContent = csvContent.replaceAll(", ", ",");
            let data = dsvFormat(",").parse(csvContent, autoType) as Row[];
            for (let i in data) {
                //r[i].temp += 273.15;
                data[i].time /= 1000;
            }
            let r = new Array(data.length);
            for(let obj in data)
            {
                console.log(obj);
                let _obj = JSON.parse(JSON.stringify(data[obj]));
                _obj.altitude = calcAltitude(_obj.press, data[0].temp+273.15);
                _obj.altura = calcAltura(_obj.press, data[0].press, data[0].temp+273.15);
                r[obj] = _obj
            }
            return r;
        } else {
            throw new Error(csvContent);
        }
    }
</script>

<Container fluid color="dark-subtle">
    {#await fetchData()}
        <Row class="justify-content-center">
            <Col xs="auto" color="transparent">
                <Spinner type="border" color="primary" />
            </Col>
        </Row>
    {:then data}
        <Row class="justify-content-center">
            <Col color="dark">
                <Plot grid frame axes height={400} implicitScales={true}>
                    <Line {data} y="temp" x="time" />
                </Plot>
            </Col>
            <Col>
                <Plot grid frame axes height={400} implicitScales={true}>
                    <Line {data} y="press" x="time" />
                </Plot>
            </Col>
        </Row>

        <Row class="justify-content-center">
            <Col xs="auto" color="transparent">
                <Plot grid frame axes height={400} implicitScales={true}>
                    <Line {data} y="altitude" x="time" />
                </Plot>
            </Col>

            <Col xs="auto" color="transparent">
                <Plot grid frame axes height={400} implicitScales={true}>
                    <Line {data} y="altura" x="time" />
                </Plot>
            </Col>
        </Row>

        <Row class="justify-content-center">
            <Map />
        </Row>
    {/await}
</Container>
