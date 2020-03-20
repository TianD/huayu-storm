import React, {Component} from 'react';
import {Button, Card, Col, Row} from 'antd';

const {Meta} = Card;

class MyCard extends Component {

    componentDidMount() {

    }

    render() {
        return (
            <Card
                hoverable
                style={{width: 280, margin: (10, 10, 10, 10)}}
                type={"inner"}
                cover={
                    <img
                        alt="example"
                        //todo use global url
                        src={"http://localhost:5000/api/get_thumbnail?preview=" + this.props.shot["preview"]}
                    />
                }
                onClick={(event) => this.props.onClick(event)}
            >
                <Row>
                    <Col span={8}><Button type={"link"}>{this.props.shot["label"]}</Button></Col>
                    {/* <Col span={8} offset={8}><Button type={"link"}>Tree01</Button></Col> */}
                </Row>
            </Card>
        )
    }
}

export default MyCard