import { useEffect, useState } from "react"
import Plot from "react-plotly.js"

async function load_data(organism, location) {
    console.log("Loading data for organism:", organism, ' and location:', location)  // Debugging statement
    // set with parameter
    const params = new URLSearchParams({
        organism: organism,
        location: location
    })
    const url = `http://localhost:8000/amr?${params}`

    const result = await fetch(url)
    const json_result = await result.json()

    return json_result
}


function AMR() {
    // initialize state variables
    const [data, setData] = useState(null)
    const [selectedOrganism, setSelectedOrganism] = useState('All Organisms')
    const [selectedLocation, setSelectedLocation] = useState("Indianapolis,Indiana")

    // fetch data
    useEffect(() => {
        const fetchData = async (selectedOrganism, selectedLocation) => {
            const result = await load_data(selectedOrganism, selectedLocation)
            setData(result)
        }
        fetchData(selectedOrganism, selectedLocation)
    }, [selectedOrganism, selectedLocation])

    return (
        <>
        <div style={{alignItems: "center", textAlign: "center"}}>
            <h3>Antibiotic Resistance Overview</h3>
        </div>

        <div className='plot-container'>
            <div className='plot-grid'>
                
                {/*Create organism selection*/}
                <div>
                    <form>
                        <label>Choose an organism:
                            <select value={selectedOrganism} onChange={(e) => setSelectedOrganism(e.target.value)}>
                                <option value='All Organisms'>All Organisms</option>
                                {data && data.organisms.map((organism) => (
                                    <option key={organism} value={organism}>{organism}</option>
                                ))}
                            </select>
                        </label>
                    </form>

                    {data && (
                        <Plot
                            data={[
                                {
                                    x: Object.keys(data.drug_class_counts),
                                    y: Object.values(data.drug_class_counts),
                                    type: 'bar'
                                }
                            ]}
                            layout={{
                                title: {
                                    text: `Number of Samples by Drug Class Resistance<br>(${selectedOrganism})`
                                },
                                xaxis: {
                                    title: {
                                        text: 'Drug Class'
                                    }
                                },
                                yaxis: {
                                    title: {
                                        text: 'Number of Samples'
                                    }
                                },
                                margin: {
                                    t: 35,
                                    b: 100
                                }
                            }}
                        />
                    )}
                </div>

                {/*Create location selection*/}
                <div>
                    <form>
                        <label>Choose a Location:
                            <select value={selectedLocation} onChange={(e) => setSelectedLocation(e.target.value)}>
                                {data && data.locations.map((location) => (
                                    <option key={location} value={location}>{location}</option>
                                ))}
                            </select>
                        </label>
                    </form>

                    {data && (
                        <Plot
                            data={[
                                {
                                    x: Object.keys(data.location_gene_counts),
                                    y: Object.values(data.location_gene_counts),
                                    type: 'bar'
                                }
                            ]}
                            layout={{
                                title: {
                                    text: `Number of Samples by Gene in ${selectedLocation}`
                                },
                                xaxis: {
                                    title: {
                                        text: 'Gene'
                                    }
                                },
                                yaxis: {
                                    title: {
                                        text: 'Number of Samples'
                                    }
                                },
                                margin: {
                                    t: 35,
                                    b: 100
                                }
                            }}
                        />
                    )}
                </div>
            </div>
        </div> 
    </>
    )
}

export default AMR