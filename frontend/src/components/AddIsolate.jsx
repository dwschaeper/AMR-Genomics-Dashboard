import { useState } from 'react'

function AddIsolate() {
    // function updating values in formData
    function valueChange(e) {
        setFormData(prev => ({...prev, [e.target.name]: e.target.value}))
    }

    // function to submit form
    async function submitForm(e) {
        e.preventDefault() // prevent page refresh on form submission

        const response = await fetch('http://localhost:8000/add_isolate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        })

        if (!response.ok) {
            console.error("Failed to submit:", response.status)
            setResponseMessage(`Failed to submit: ${response.status}`)
            return
        }

        const result = await response.json()
        console.log(result)
        setResponseMessage(result.message)
    }

    // initialize state variables
    const [formData, setFormData] = useState({
        sample_id: '',
        city: '',
        state: '',
        latitude: '',
        longitude: '',
        organism: '',
        collection_date: '',
        num_contigs: '',
        amr_gene: '',
        drug_class: '',
        phenotype: ''
    })
    const [responseMessage, setResponseMessage] = useState('')

    return (
        <>
        <div className='dashboard-container'>
            <div>
                <h3 style={{textAlign: 'left'}}>
                Use this form to add a new sample to the database. Please ensure all fields are correctly filled out before submission.
                </h3>
                <form onSubmit={submitForm}>
                    <h4>Metadata</h4>
                    <label>
                        Sample ID:
                        <input value={formData.sample_id} onChange={valueChange} type="text" name="sample_id" placeholder="Sample ID" required />
                    </label>
                    <label>
                        Organism:
                        <input value={formData.organism} onChange={valueChange} type="text" name="organism" placeholder="Organism" required />
                    </label>
                    <label>
                        City:
                        <input value={formData.city} onChange={valueChange} type="text" name="city" placeholder="City" required />
                    </label>
                    <label>
                        State:
                        <input value={formData.state} onChange={valueChange} type="text" name="state" placeholder="State" required />
                    </label>
                    <label>
                        Latitude:
                        <input value={formData.latitude} onChange={valueChange} type="number" name="latitude" placeholder="Latitude" step="any" required />
                    </label>
                    <label>
                        Longitude:
                        <input value={formData.longitude} onChange={valueChange} type="number" name="longitude" placeholder="Longitude" step="any" required />
                    </label>
                    <br></br>
                    <br></br>
                    <label>
                        Collection Date:
                        <input value={formData.collection_date} onChange={valueChange} type="date" name="collection_date" required />
                    </label>
                    
                    <h4>Sample Data</h4>
                    <label>
                        Number of Contigs:
                        <input value={formData.num_contigs} onChange={valueChange} type="number" name="num_contigs" placeholder="Number of Contigs" required />
                    </label>

                    <h4>AMR Gene Annotations</h4>
                    <label>
                        AMR Gene:
                        <textarea value={formData.amr_gene} onChange={valueChange} name="amr_gene" placeholder="AMR Gene" />
                    </label>
                    <label>
                        Drug Class:
                        <textarea value={formData.drug_class} onChange={valueChange} name="drug_class" placeholder="Drug Class" />
                    </label>
                    <label>
                        Phenotype:
                        <textarea value={formData.phenotype} onChange={valueChange} name="phenotype" placeholder="Phenotype" />
                    </label>
                    <br></br>
                    <br></br>
                    <button type="submit">Add Isolate</button>
                </form>

                <p><em>{responseMessage}</em></p>
            </div>
        </div>
        </>
    )
}

export default AddIsolate