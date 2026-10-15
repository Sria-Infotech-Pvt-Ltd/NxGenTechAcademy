import { useState } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { toast } from "sonner";
import axiosInstance from "@/api/axiosInstance";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";

interface DemoFormProps {
    defaultCourse?: string;
    onSuccess?: () => void;
}

const COURSES = [
    "SAP Technical & Development",
    "SAP Functional Modules",
    "SAP Business Technology Platform (BTP)",
    "SAP Specialized / Sub Courses",
    "Data Analytics",
    "Python",
    "Digital Marketing",
    "AI",
    "AIML",
    "Power BI"
];

const DemoForm = ({ defaultCourse, onSuccess }: DemoFormProps) => {
    const courseOptions = [...COURSES];
    if (defaultCourse && !courseOptions.includes(defaultCourse)) {
        courseOptions.unshift(defaultCourse);
    }

    const [formData, setFormData] = useState({
        full_name: "",
        email: "",
        phone: "",
        course: defaultCourse || courseOptions[0],
    });
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSelectChange = (name: string, value: string) => {
        setFormData({
            ...formData,
            [name]: value,
        });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);

        // Map to the backend expected fields with defaults for the ones removed from UI
        const payload = {
            ...formData,
        };

        try {
            await axiosInstance.post("/api/leads/schedule-demo/", payload);
            toast.success("Demo request submitted successfully!");
            onSuccess?.();
        } catch (error: any) {
            console.error("Demo Request Error:", error);
            if (error.response?.status === 429) {
                toast.error("Too many requests. Please wait a moment before submitting again.");
            } else {
                const errorMsg = error.response?.data?.message || "Something went wrong. Please try again.";
                toast.error(errorMsg);
            }
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-4">
                <div className="space-y-2">
                    <Label htmlFor="demo-full_name" className="text-sm font-semibold text-gray-700">Full Name</Label>
                    <Input
                        id="demo-full_name"
                        name="full_name"
                        placeholder="Enter your name"
                        value={formData.full_name}
                        onChange={handleChange}
                        required
                        className="h-11"
                    />
                </div>

                <div className="space-y-2">
                    <Label htmlFor="demo-email" className="text-sm font-semibold text-gray-700">Email Address</Label>
                    <Input
                        id="demo-email"
                        name="email"
                        type="email"
                        placeholder="Enter your email"
                        value={formData.email}
                        onChange={handleChange}
                        required
                        className="h-11"
                    />
                </div>

                <div className="space-y-2">
                    <Label htmlFor="demo-phone" className="text-sm font-semibold text-gray-700">Phone Number</Label>
                    <Input
                        id="demo-phone"
                        name="phone"
                        type="tel"
                        placeholder="Enter phone number"
                        value={formData.phone}
                        onChange={handleChange}
                        required
                        className="h-11"
                    />
                </div>

                <div className="space-y-2">
                    <Label className="text-sm font-semibold text-gray-700">Course</Label>
                    <Select
                        value={formData.course}
                        onValueChange={(value) => handleSelectChange("course", value)}
                        required
                    >
                        <SelectTrigger className="h-11 border-gray-200">
                            <SelectValue placeholder="Select a course" />
                        </SelectTrigger>
                        <SelectContent>
                            {courseOptions.map((course) => (
                                <SelectItem key={course} value={course}>
                                    {course}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>
            </div>
            <div className="pt-2">
                <Button
                    type="submit"
                    className="w-full bg-[#000080] hover:bg-[#000080]/90 text-white font-bold h-12 text-lg shadow-md transition-all rounded-md"
                    disabled={isSubmitting}
                >
                    {isSubmitting ? "Submitting..." : "Submit"}
                </Button>
            </div>
        </form>
    );
};

export default DemoForm;
