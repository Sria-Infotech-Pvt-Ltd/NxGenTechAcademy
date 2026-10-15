import axiosInstance from "@/api/axiosInstance";

export interface CourseContext {
  name: string;
  slug: string;
}

export interface ChatbotResponse {
  found: boolean;
  reply: string;
  course?: string | null;
  course_name?: string | null;
  course_slug?: string | null;
  section?: string | null;
  similarity?: number;
  source_file?: string | null;
  db_id?: number | null;
  action_type?: string | null;
  action_url?: string | null;
  action_text?: string | null;
  error?: string;
}

export const chatbotService = {
  searchKnowledgeBase: async (
    query: string,
    courseContext?: CourseContext | null
  ): Promise<ChatbotResponse> => {
    const payload: { query: string; course_context?: CourseContext } = {
      query: query.trim(),
    };
    if (courseContext && courseContext.name && courseContext.slug) {
      payload.course_context = {
        name: courseContext.name.trim(),
        slug: courseContext.slug.trim(),
      };
    }
    const response = await axiosInstance.post<ChatbotResponse>("/api/chatbot/search/", payload);
    return response.data;
  },
};

