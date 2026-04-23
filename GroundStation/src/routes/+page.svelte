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
            csvContent = "packet, time, temp, press, humidity\n".concat(`
            0, 6931, 22.645706, 100025.11, 61.29105
            1, 7471, 22.633628, 100025.692, 61.290812, 4, 0.015625, 0.0078125, -0.0390625
            0, 7891, 22.580234, 100021.912, 61.260308
            0, 8684, 22.602482, 100023.68, 61.221436
            1, 9078, 22.555444, 100020.28, 61.174724, 3, 0.1328125, -0.1640625, 0.04296875
            0, 9476, 22.5465452, 100026.97, 61.191136
            0, 10218, 22.598034, 100026.26, 61.221036
            1, 10589, 22.55481, 100023.984, 61.258904, 3, 0.01953125, -0.015625, 0.0
            0, 11115, 22.52112, 100024.31, 61.269096
            1, 11885, 22.598668, 100023.99, 61.32257, 3, 0.01953125, 0.0, -0.171875
            0, 12873, 22.596126, 100022.31, 61.45228
            1, 13293, 22.54909, 100023.89, 61.45076, 3, -0.1171875, 0.015625, -0.0390625
            0, 13815, 22.53002, 100024.08, 61.47282
            1, 14611, 22.592312, 100021.82, 61.474284, 3, 0.171875, -0.0859375, -0.0234375
            0, 15750, 22.564978, 100028.05, 61.41684
            1, 16165, 22.51095, 100027.668, 61.403576, 3, 0.03515625, 0.0078125, 0.191406252
            0, 16661, 22.486796, 100020.26, 61.3856
            1, 17463, 22.542098, 100024.75, 61.319624, 3, -0.03515625, 0.01953125, -0.0234375
            0, 18572, 22.509678, 100022.488, 61.289944
            1, 19023, 22.442936, 100027.03, 61.28231, 3, 0.08984375, 0.0, 0.0390625
            0, 19495, 22.423866, 100017.91, 61.29832
            1, 20383, 22.455014, 100023.69, 61.28218, 3, -0.0078125, -0.0390625, 0.1015625
            0, 21482, 22.449928, 100027.39, 61.241696
            1, 21922, 22.3812784, 100021.912, 61.228116, 3, 0.11328125, -0.0390625, -0.09765625
            0, 22405, 22.348862, 100023.668, 61.221332
            1, 23243, 22.399076, 100021.912, 61.23376, 3, 0.09765625, -0.11328125, 0.0
            0, 24409, 22.353946, 100024.03, 61.260076
            1, 24826, 22.310088, 100023.52, 61.2927, 3, -0.09375, 0.0546875, -0.12890625
            0, 25345, 22.282754, 100022.61, 61.325456
            1, 26151, 22.360302, 100024.24, 61.412796, 3, 0.1796875, -0.078125, 0.0234375
            0, 27230, 22.35331, 100024.22, 61.536524
            1, 27652, 22.307544, 100022.8, 61.580124, 3, -0.1328125, -0.0390625, -0.15234375
            0, 28255, 22.284026, 100025.63, 61.64688
            1, 29075, 22.343776, 100020.45, 61.688164, 3, -0.0390625, -0.0390625, 0.0
            0, 30233, 22.331064, 100024.17, 61.721592
            1, 30658, 22.289112, 100027.912, 61.7371136, 3, 0.0078125, -0.0546875, 0.046875
            0, 31191, 22.264322, 100024.65, 61.77549
            1, 32009, 22.333606, 100022.42, 61.783528, 3, -0.109375, 0.06640625, 0.0078125
            0, 33232, 22.326614, 100023.4, 61.86231
            1, 33651, 22.285932, 100025.16, 61.877748, 3, -0.1171875, -0.03125, -0.078125
            0, 34137, 22.263686, 100025.87, 61.90546
            1, 34954, 22.33297, 100021.14, 61.90718, 3, 0.183593744, -0.0859375, 0.140625
`);
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
                _obj.entropia = 0
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
            <Col xs="auto" color="transparent">
                <Plot grid frame axes height={400} implicitScales={true}>
                    <Line {data} y="temp" x="time" />
                </Plot>
            </Col>
            <Col xs="auto" color="transparent">
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
            <Col xs="auto" color="transparent">
                <Plot grid frame axes height={400} implicitScales={true}>
                    <Line {data} y="entropia" x="time" />
                </Plot>
            </Col>
        </Row>

        <Row class="justify-content-center">
            <!--Map /-->
        </Row>
    {/await}
</Container>
