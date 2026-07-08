import { useEffect, useState } from "react"
import Plot from "react-plotly.js"

import '../App.css'

async function load_data() {
    const overview_url = 'http://localhost:8000/overview'

    const result = await fetch(overview_url)
    const json_result = await result.json()

    return json_result
}


function Overview() {
    // initialize state variables
    const [data, setData] = useState(null)

    // fetch data
    useEffect(() => {
        const fetchData = async () => {
            const result = await load_data()
            setData(result)
        }
        fetchData()
    }, [])

    return(
        <>
        <div className='dashboard-container'>
            <div>
                <p>This dashboard provides an overview of bacterial genomic
                surveillance data, integrating isolate metadata, genome
                assembly statistics, and antimicrobial resistance annotations.
                Explore organism distributions, geographic trends, and AMR
                profiles across collected samples.
                </p>
            </div>
        
            <div style={{display: "flex", justifyContent: "center", padding: '20px'}}>
                <table>
                    <thead>
                        <th style={{padding: '10px'}}>Total Samples</th>
                        <th style={{padding: '10px'}}>Total Organisms</th>
                        <th style={{padding: '10px'}}>Unique Locations</th>
                        <th style={{padding: '10px'}}>AMR Calls</th>
                        <th style={{padding: '10px'}}>Unique AMR Genes</th>
                    </thead>
                    <tbody>
                        <tr>
                            <td style={{textAlign: 'center'}}>{data ? data.num_samples : 'Loading...'}</td>
                            <td style={{textAlign: 'center'}}>{data ? data.num_organisms : 'Loading...'}</td>
                            <td style={{textAlign: 'center'}}>{data ? data.num_locations : 'Loading...'}</td>
                            <td style={{textAlign: 'center'}}>{data ? data.num_amr_calls : 'Loading...'}</td>
                            <td style={{textAlign: 'center'}}>{data ? data.num_amr_genes : 'Loading...'}</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div style={{alignItems: "center", textAlign: "center"}}>
                <h3>Contents Overview Plots</h3>
            </div>

            <div className='plot-container'>
                {/*Create first fig*/}
                <div style={{ display: 'flex', justifyContent: 'center'}}>
                    <div style={{ flex: 1, textAlign: 'center', padding: '10px'}}>
                        {data && (
                            <Plot
                                data={[
                                    {
                                        x: Object.keys(data.organisms),
                                        y: Object.values(data.organisms),
                                        type: 'bar'
                                    }
                                ]}
                                layout={{
                                    title: {
                                        text: 'Number of Samples by Organism'
                                    },
                                    xaxis: {
                                        title: {
                                            text: 'Organism'
                                        }
                                    },
                                    yaxis: {
                                        title: {
                                            text: 'Number of Samples'
                                        }
                                    },
                                    margin: {
                                        b: 150,
                                        t: 25
                                    },
                                    height: 600,
                                    width: 700
                                }}
                            />
                        )}
                    </div>
                    
                    {/*Create second fig*/}
                    <div style={{ flex: 1, textAlign: 'center', padding: '10px' }}>
                        {data && (
                            <Plot
                                data={[
                                    {
                                        x: Object.keys(data.locations),
                                        y: Object.values(data.locations),
                                        type: 'bar'
                                    }
                                ]}
                                layout={{
                                    title: {
                                        text: 'Number of Samples by Location'
                                    },
                                    xaxis: {
                                        title: {
                                            text: 'Location (City, State)',
                                            standoff: 40
                                        }
                                    },
                                    yaxis: {
                                        title: {
                                            text: 'Number of Samples'
                                        }
                                    },
                                    margin: {
                                        b: 100,
                                        t: 25
                                    },
                                    height: 600,
                                    width: 700,
                                }}
                            />
                            )}
                    </div>
                </div>
            </div>
        </div>
        </>
    )
}

export default Overview